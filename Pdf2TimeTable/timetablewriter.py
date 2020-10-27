import numpy as np
from pandas import ExcelWriter, DataFrame
from pprint import pprint

daysOfWeek = [
        "Lundi",
        "Mardi",
        "Mercredi",
        "Jeudi",
        "Vendredi",
        "Samedi",
        "Dimanche"]

class TimeTableWriter():
    def __init__(self, debug):
        self.debug = debug

    def get_gaps_list(self, intervals):
        startIndex = next((index for index,interval in enumerate(intervals) if interval[0]))
        endIndex = len(intervals)-next((index for index,interval in enumerate(intervals[::-1]) if interval[0]))-1
        tmp = intervals[startIndex:endIndex+1]
        gaps_entries_and_exits = [ interval for index,interval in enumerate(tmp) if index < len(tmp)-1 and interval[0] != tmp[index+1][0] ]
        array = np.array(gaps_entries_and_exits).reshape(-1,4)
        gaps = [(interval[1][1],interval[3][1]) for interval in array]
        return gaps

    def prepare_data(self, subjects_per_intervals_per_days_week_a, subjects_per_intervals_per_days_week_b):
        data = {'Week A':{},'Week B':{}}
        for week,subjects_per_intervals_per_days in zip(data.keys(),
            [subjects_per_intervals_per_days_week_a, subjects_per_intervals_per_days_week_b]):
            for day,intervals in subjects_per_intervals_per_days.items():
                start = next((interval for filled,interval in intervals if filled))[0]
                end = next((interval for filled,interval in intervals[::-1] if filled))[1]
                gaps = self.get_gaps_list(intervals)
                if self.debug:
                    print()
                    print(day, start, end, gaps)

                data[week][day] = (start,end,gaps)
        if self.debug:
            pprint(data)
        return data

    def write_prepared_data_to_excel(self, name, prepared_data, output_file):
        max_gaps_count = 0
        for _,data in prepared_data.items():
            for _,day in data.items():
                max_gaps_count = max(max_gaps_count, len(day[2]))

        array = np.ndarray(shape=(max_gaps_count+4, len(daysOfWeek)*4), dtype="U18")
        array.fill('')
        array[0][0] = name
        currentColumn = 0
        for week_str,week_key in zip(['Semaine A', 'Semaine B'], prepared_data.keys()):
            lastDayOfWeekIndex = -1
            for day,day_data in prepared_data[week_key].items():
                if not day in daysOfWeek:
                    print("Day "+day+" doesn't exist..., anyway")
                    continue
                else:
                    currentDayOfWeekIndex = daysOfWeek.index(day)
                    if currentDayOfWeekIndex < lastDayOfWeekIndex:
                        print("Please order by date")
                        break
                    while lastDayOfWeekIndex+1 < currentDayOfWeekIndex:
                        currentDay = daysOfWeek[lastDayOfWeekIndex+1]
                        print("Adding "+currentDay)
                        array[1][currentColumn] = currentDay+' '+week_str
                        array[2][currentColumn] = "0h00"
                        array[3][currentColumn] = "0h00"
                        lastDayOfWeekIndex += 1
                        currentColumn += 2
                    lastDayOfWeekIndex = currentDayOfWeekIndex
                array[1][currentColumn] = day+' '+week_str
                array[2][currentColumn] = day_data[0]
                for index,gap in enumerate(day_data[2]):
                    array[index+3][currentColumn] = gap[0]
                    array[index+3][currentColumn+1] = gap[1]
                array[len(day_data[2])+3][currentColumn] = day_data[1]
                currentColumn += 2

        with ExcelWriter(output_file) as writer:
            pd_df = DataFrame(array)
            if self.debug: print(pd_df)
            pd_df.to_excel(writer, sheet_name="Sheet 1", index=False, header=False)

    def write_excel(self, name, subjects_per_intervals_per_days_week_a, subjects_per_intervals_per_days_week_b, output_file):
        prepared_data = self.prepare_data(subjects_per_intervals_per_days_week_a, subjects_per_intervals_per_days_week_b)
        self.write_prepared_data_to_excel(name, prepared_data, output_file)



