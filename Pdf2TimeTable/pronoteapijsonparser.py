from datetime import datetime
from dateutil.parser import isoparse
from pprint import pprint
import json
import pytz

class PronoteApiJsonParser():
    def __init__(self, debug):
        self.debug = debug

    def str2date(self, time):
        ParisTZ = pytz.timezone('Europe/Paris')
        return self.clean_time(isoparse(time).astimezone(ParisTZ).strftime("%Hh%M"))

    def week(self, time):
        return isoparse(time).weekday()

    def clean_time(self, time):
        if time[0] == '0':
            time = time[1:]
        corrections = {
                '10h05':'10h20',
                '10h10':'10h20',
                '11h10':'11h20',
                '12h20':'12h15',
                '14h35':'14h50',
                '14h40':'14h50',
                '15h40':'15h50',
                '17h50':'17h45',
                '19h45':'19h35',
        }
        if time in corrections:
            return corrections[time]
        return time
    def update_value(self, dict_timetable, day, value):
        if day in dict_timetable.keys():
            dict_timetable[day] += [value]
        else:
            dict_timetable[day] = [value]

    def raw_list2writer_data(self, raw_list):
        start = raw_list[0][0]
        end = raw_list[-1][1]
        gaps =  [
                    (interval[1], raw_list[index+1][0])
                    for index,interval in enumerate(raw_list)
                    if index+1 < len(raw_list)
                        and interval[1] != raw_list[index+1][0]
                ]
        return (start,end,gaps)

    def parse(self, json_file):
        data = json.loads(open(json_file, 'r').read())
        name = data["name"].split(' ')[1]
        timetable = data["timetable"]
        daysOfWeek = [
                "Lundi",
                "Mardi",
                "Mercredi",
                "Jeudi",
                "Vendredi",
                "Samedi",
                "Dimanche"]
        cleaned_timetable = [ (daysOfWeek[self.week(day['from'])], self.str2date(day['from']), self.str2date(day['to'])) for day in timetable ]
        dict_timetable = {}
        [ self.update_value(dict_timetable, day, (from_date, to_date)) for day,from_date,to_date in cleaned_timetable ]

        [ dict_timetable.update({k:self.raw_list2writer_data(t)}) for k,t in dict_timetable.items() ]
        return (name,dict_timetable)
