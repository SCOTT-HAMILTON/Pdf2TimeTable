import click
from Pdf2TimeTable.pronoteapijsonparser import PronoteApiJsonParser
from Pdf2TimeTable.timetableparser import TimeTableParser
from Pdf2TimeTable.timetablewriter import TimeTableWriter
from enum import Enum
from json import load
from os import environ
from os.path import isfile
from pprint import pprint

class Method(Enum):
    JSON2TIMETABLE  = 1
    MAKE_CSV        = 2
    CSV2TIMETABLE   = 3
    ALL             = 4

class ChoiceMethod():
    def __init__(self, method,
            json_week_a=None,json_week_b=None, # Options for JSON2TIMETABLE
            input_pdf_week_a=None, input_pdf_week_b=None, output_csv=None, # Options for MAKE_CSV and ALL
            input_csv_week_a=None, input_csv_week_b=None, # Options for CSV2TIMETABLE
            name=None, # Options for CSV2TIMETABLE and ALL
            output_timetable=None): # Options for JSON2TIMETABLE, CSV2TIMETABLE and ALL
        self.method = method
        if self.method == Method.JSON2TIMETABLE:
            if json_week_a == None:
                print("Error, can't convert json to timetable without an input json file for week A")
                return
            if json_week_b == None:
                print("Error, can't convert json to timetable without an input json file for week B")
                return
            if output_timetable == None:
                print("Error, can't convert json to timetable without the output file")
                return
            self.json_week_a = json_week_a
            self.json_week_b = json_week_b
            self.output_timetable = output_timetable
        elif self.method in (Method.MAKE_CSV, Method.ALL):
            if input_pdf_week_a == None:
                print("Error, can't make csv without an input pdf for week A")
                return
            if input_pdf_week_b == None:
                print("Error, can't make csv without an input pdf for week B")
                return
            if output_csv == None:
                print("Error, can't make csv without an output csv")
                return
            self.input_pdf_week_a = input_pdf_week_a
            self.input_pdf_week_b = input_pdf_week_b
            self.output_csv = output_csv
            if self.method == Method.ALL:
                if name == None:
                    print("Error, can't make a timetable without a name")
                    return
                if output_timetable == None:
                    print("Error, can't make a timetable without the output file")
                    return
                self.name = name
                self.output_timetable = output_timetable
        elif self.method == Method.CSV2TIMETABLE:
            if input_csv_week_a == None:
                print("Error, can't make csv without an input pdf for week A")
                return
            if input_csv_week_b == None:
                print("Error, can't make csv without an input pdf for week B")
                return
            if name == None:
                print("Error, can't make a timetable without a name")
                return
            if output_timetable == None:
                print("Error, can't make a timetable without the output file")
                return
            self.input_csv_week_a = input_csv_week_a
            self.input_csv_week_b = input_csv_week_b
            self.name = name
            self.output_timetable = output_timetable
        else:
            print("Error, unknown method : ",method)


class ChoiceMethodParamType(click.ParamType):
    name = """  json2timetable <json_week_a> <json_week_b> <output_timetable> |
                 make_csv <input_pdf_week_a> <input_pdf_week_b> <output_csv> |
                 csv2timetable <input_csv_week_a> <input_csv_week_b> <name> <output_timetable> |
                 all <input_pdf_week_a> <input_pdf_week_b> <output_csv> <name> <output_timetable>"""

    def convert(self, value, param, ctx):
        print("converting...")
        if value[:15] == 'json2timetable ':
            # Parse make_csv
            print("Parse json2timetable")
            arg = value[15:]
            args = arg.split(' ')
            if len(args) != 3:
                if len(args) == 1:
                    self.fail(
                        "json2timetable needs 3 arguments but "+str(len(args))+" was provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
                else:
                    self.fail(
                        "json2timetable needs 3 arguments but "+str(len(args))+" were provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
            return ChoiceMethod(Method.JSON2TIMETABLE,
                    json_week_a=args[0],
                    json_week_b=args[1],
                    output_timetable=args[2])
        if value[:9] == 'make_csv ':
            # Parse make_csv
            print("Parse make_csv")
            arg = value[9:]
            args = arg.split(' ')
            if len(args) != 3:
                if len(args) == 1:
                    self.fail(
                        "make_csv needs 3 arguments but "+str(len(args))+" was provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
                else:
                    self.fail(
                        "make_csv needs 3 arguments but "+str(len(args))+" were provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
            return ChoiceMethod(Method.MAKE_CSV,
                    input_pdf_week_a=args[0],
                    input_pdf_week_b=args[1],
                    output_csv=args[2])
        elif value[:14] == 'csv2timetable ':
            # Parse csv2timetable
            print("Parse csv2timetable")
            arg = value[14:]
            args = arg.split(' ')
            if len(args) != 4:
                if len(args) == 1:
                    self.fail(
                        "csv2timetable needs 4 arguments but "+str(len(args))+" was provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
                else:
                    self.fail(
                        "csv2timetable needs 4 arguments but "+str(len(args))+" were provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
            return ChoiceMethod(Method.CSV2TIMETABLE,
                    input_csv_week_a=args[0],
                    input_csv_week_b=args[1],
                    name=args[2],
                    output_timetable=args[3])
        elif value[:4] == 'all ':
            # Parse csv2timetable
            print("Parse all")
            arg = value[4:]
            args = arg.split(' ')
            if len(args) != 5:
                if len(args) == 1:
                    self.fail(
                        "all needs needs 5 arguments but "+str(len(args))+" was provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
                else:
                    self.fail(
                        "all needs 5 arguments but "+str(len(args))+" were provided : "
                        f"{value!r} of type {type(value).__name__}",
                        param,
                        ctx,
                    )
            return ChoiceMethod(Method.ALL,
                    input_pdf_week_a=args[0],
                    input_pdf_week_b=args[1],
                    output_csv=args[2],
                    name=args[3],
                    output_timetable=args[4])
        else:
            self.fail(
                "Method unknown, couldn't parse argument."
                f"{value!r} of type {type(value).__name__}",
                param,
                ctx,
            )

@click.command()
@click.option('-d', '--debug', is_flag=True)
@click.option('-m', '--method', type=ChoiceMethodParamType(), required=True)
def cli(method, debug):
    """Converts a pdf timetable (generated by pronote)  to an excel timetable (that can be used with TimeTable2Header)"""
    if method == None:
        return 1
    # config_file = environ['HOME']+'/.config/pronotebot.conf'
    # assert isfile(config_file)
    # config = load(open(config_file, 'r'))
    if method.method == Method.JSON2TIMETABLE:
        jsonparser = PronoteApiJsonParser(debug)
        writer = TimeTableWriter(debug)
        name,weekA = jsonparser.parse(method.json_week_a)
        _,weekB = jsonparser.parse(method.json_week_b)
        prepared_data = {
                'Week A':weekA,
                'Week B':weekB}
        if debug:
            pprint(prepared_data)
        writer.write_prepared_data_to_excel(name, prepared_data, method.output_timetable)
        print("output file is `"+method.output_timetable+"`")
    elif method.method == Method.MAKE_CSV:
        parser = TimeTableParser(debug)
        parser.decrypt_pdf(method.input_pdf_week_a, "out_a.pdf")
        parser.decrypt_pdf(method.input_pdf_week_b, "out_b.pdf")
        parser.extract_table_from_pdf("out_a.pdf", method.output_csv[::-1][4:][::-1]+"week_a.csv")
        parser.extract_table_from_pdf("out_b.pdf", method.output_csv[::-1][4:][::-1]+"week_b.csv")
    elif method.method == Method.CSV2TIMETABLE:
        parser = TimeTableParser(debug)
        writer = TimeTableWriter(debug)
        writer.write_excel( method.name,
                            parser.parse_csv(method.input_csv_week_a),
                            parser.parse_csv(method.input_csv_week_b),
                            method.output_timetable)
        print("output file is `"+method.output_timetable+"`")
    elif method.method == Method.ALL:
        parser = TimeTableParser(debug)
        parser.decrypt_pdf(method.input_pdf_week_a, "out_a.pdf")
        parser.decrypt_pdf(method.input_pdf_week_b, "out_b.pdf")
        csv_file_a = method.output_csv[::-1][4:][::-1]+"_week_a.csv"
        csv_file_b = method.output_csv[::-1][4:][::-1]+"_week_b.csv"
        parser.extract_table_from_pdf("out_a.pdf", csv_file_a)
        parser.extract_table_from_pdf("out_b.pdf", csv_file_b)
        writer = TimeTableWriter(debug)
        writer.write_excel( method.name,
                            parser.parse_csv(csv_file_a),
                            parser.parse_csv(csv_file_b),
                            method.output_timetable)
        print("output file is `"+method.output_timetable+"`")
