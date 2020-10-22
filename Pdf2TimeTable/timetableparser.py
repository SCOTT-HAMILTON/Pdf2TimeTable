# from pdfplumber import open as pdfplumber_open
from PyPDF2 import PdfFileWriter, PdfFileReader
from tabula import read_pdf, convert_into
from pandas import read_csv
from re import search
from math import isnan
import numpy as np

class TimeTableParser():
    def __init__(self, debug=False):
        self.debug = debug
        self.dt = np.dtype([('pos', np.uintc), ('time', np.unicode_, 6), ])

    def decrypt_pdf(self, pdf_file, output_file):
        """PDF from pronote are encrypted with an empty password"""
        out = PdfFileWriter()
        file = PdfFileReader(pdf_file)
        password = ""
        if file.isEncrypted:
            file.decrypt(password)
            for idx in range(file.numPages):
                page = file.getPage(idx)
                out.addPage(page)
            with open(output_file, "wb") as f:
                out.write(f)
            if self.debug: print("File decrypted Successfully.")
        else:
            if self.debug: print("File already decrypted.")

    def extract_table_from_pdf(self, pdf_file, csv_output_file):
        """Extract table from pdf and write it to csv"""
        dfs = read_pdf(pdf_file, pages="all")
        convert_into(pdf_file, csv_output_file, output_format="csv", pages='all')

    def clean_time(self, time):
        if time == None or (isinstance(time, float) and isnan(time)):
            return ""
        s = search("([0-9]{1,2}h[0-9]{2})", time)
        if s:
            return s.string[s.span()[0]:s.span()[1]]
        else:
            if self.debug: print("No match with `"+time+"` ?")
            return ""

    def make_times_pos(self, dfs_transposed):
        times_pos = {}
        pos = 0
        for time in map(self.clean_time, dfs_transposed[0]):
            if time != '':
                times_pos[pos] = time
            pos += 1
        return times_pos


    def make_time_intervals(self, times_pos):
        times = list(times_pos.items())
        array = np.array(times, dtype=self.dt)
        s = array[0] # Save the start of the array
        e = array[-1] # Save the end of the array
        array = array[1:array.shape[0]-1] # Remove the first and the last element
        array = np.array( # Convert the list back to np.array
                        [s]+ # Introduce back first element
                        list( # Convert to list
                            map(lambda x: x[0], # Function to convert [[(a,b)],[(c,d)]] to [(a,b),(c,d)]
                                np.dstack((array, array.copy()))[0].reshape(-1,1))) # Make a copy and zip the original with the copy
                        +[e] # Introduce back the last element
                        , dtype=self.dt # The actual type of the data
                ) # Magick to double the elements and introduce back the first and last elements
        time_intervals = array.reshape(-1,2) # Reshape the double elements
        return time_intervals

    def get_start_and_end_of_day(self, day):
        start = next(((index,t) for index,t in enumerate(day) if isinstance(t, str)))
        (i,t) = next(((index,t) for index,t in enumerate(day[::-1]) if isinstance(t, str)))
        end = (len(day)-i-1,t)
        return (start[0],end[0])

    def start_pos_to_hour(self, pos):
        return list(time for p,time in times_pos.items() if p <= pos)[-1]

    def end_pos_to_hour(self, pos):
        return next(time for p,time in times_pos.items() if p >= pos)

    def get_texts_pos(self, day):
        return list((index,t) for index,t in enumerate(day) if isinstance(t, str))

    def pos_in_interval(self, pos, interval):
        return pos >= interval[0] and pos < interval[1]

    def parse_csv(self, csv_file):
        dfs = read_csv(csv_file)
        if self.debug: print(dfs)

        dfs_transposed = dfs.values.transpose()
        times_pos = self.make_times_pos(dfs_transposed)
        if self.debug: print("Times Pos : ",times_pos)
        time_intervals = self.make_time_intervals(times_pos)

        tmp_list = time_intervals.tolist()
        tmp_list.pop(2)
        tmp_list.pop(8)
        time_intervals = np.array(tmp_list, dtype=self.dt)
        if self.debug: print("Time Intervals : ",time_intervals)

        daysOfWeek = [
                "Lundi",
                "Mardi",
                "Mercredi",
                "Jeudi",
                "Vendredi",
                "Samedi",
                "Dimanche"]
        currentDayOfWeek = 0
        subjects_per_intervals_per_days = {}
        for d in range(1,len(dfs_transposed)):
            if not str in map(type, dfs_transposed[d]):
                # if self.debug: print("empty list, skipping...")
                continue

            texts_pos = self.get_texts_pos(dfs_transposed[d])
            if self.debug: print()
            if self.debug: print(daysOfWeek[currentDayOfWeek])
            if self.debug: print("Texts Pos : ",texts_pos)

            subjects_per_intervals = []
            for i in time_intervals:
                interval = (i[0][0],i[1][0])
                time_interval = (i[0][1],i[1][1])
                if self.debug: print(interval)
                l = list((p,text) for p,text in texts_pos if self.pos_in_interval(p, interval) )
                if len(l) > 0:
                    subjects_per_intervals.append((True, time_interval))
                else:
                    if self.debug: print("Nothing at ",interval)
                    subjects_per_intervals.append((False, time_interval))

            for interval in subjects_per_intervals:
                if self.debug: print(interval)
            subjects_per_intervals_per_days[daysOfWeek[currentDayOfWeek]] = subjects_per_intervals
            currentDayOfWeek += 1
        return subjects_per_intervals_per_days

