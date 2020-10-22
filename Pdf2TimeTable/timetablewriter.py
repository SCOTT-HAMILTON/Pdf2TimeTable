import numpy as np
from pandas import ExcelWriter, DataFrame
from pprint import pprint

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

    def write_excel(self, name, subjects_per_intervals_per_days_week_a, subjects_per_intervals_per_days_week_b, output_file):
        data = {'Week A':{},'Week B':{}}
        max_gaps_count = 0
        for week,subjects_per_intervals_per_days in zip(data.keys(),
            [subjects_per_intervals_per_days_week_a, subjects_per_intervals_per_days_week_b]):
            for day,intervals in subjects_per_intervals_per_days.items():
                start = next((interval for filled,interval in intervals if filled))[0]
                end = next((interval for filled,interval in intervals[::-1] if filled))[1]
                gaps = self.get_gaps_list(intervals)
                if self.debug:
                    print()
                    print(day, start, end, gaps)
                max_gaps_count = max(len(gaps), max_gaps_count)

                data[week][day] = (start,end,gaps)
        if self.debug:
            pprint(data)
        array = np.ndarray(shape=(max_gaps_count+4, (len(data['Week A'].keys())+len(data['Week B'].keys()))*2), dtype="U16")
        array.fill('')
        array[0][0] = name
        currentColumn = 0
        for week_str,week_key in zip(['Semaine A', 'Semaine B'], data.keys()):
            for day,day_data in data[week_key].items():
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


