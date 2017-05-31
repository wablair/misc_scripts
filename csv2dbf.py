import csv
import datetime
import getopt
import io
import struct
import sys

def print_help():
    print("csv2dbf.py -i <input file> -o <dbf output file> -c " +
      "<csv output file>")
    sys.exit()

"""
def dbfwriter() from:
https://code.activestate.com/recipes/362715-dbf-reader-and-writer/
by  Raymond Hettinger
"""

def dbfwriter(f, fieldnames, fieldspecs, records):

    """
    Return a string suitable for writing directly to a binary dbf file.

    File f should be open for writing in a binary mode.

    Fieldnames should be no longer than ten characters and not include \x00.
    Fieldspecs are in the form (type, size, deci) where
        type is one of:
            C for ascii character data
            M for ascii character memo data (real memo fields not supported)
            D for datetime objects
            N for ints or decimal objects
            L for logical values 'T', 'F', or '?'
        size is the field width
        deci is the number of decimal places in the provided decimal object
    Records can be an iterable over the records (sequences of field values).
    
    """
    # header info
    ver = 3
    now = datetime.datetime.now()
    yr = now.year - 1900
    mon = now.month
    day = now.day
    numrec = len(records)
    numfields = len(fieldspecs)
    lenheader = numfields * 32 + 33
    lenrecord = sum(field[1] for field in fieldspecs) + 1
    hdr = struct.pack(b'<BBBBLHH20x', ver, yr, mon, day, numrec, lenheader,
      lenrecord)

    f.write(hdr)
                      
    # field specs
    for name, (typ, size, deci) in zip(fieldnames, fieldspecs):
        if len(name) > 10:
            name = name[10:]
        name = name.ljust(11, '\x00')
        fld = struct.pack(b'<11sc4xBB14x', bytearray(name, 'utf-8'),
          str.encode(typ), size, deci)
        f.write(fld)

    # terminator
    f.write(b'\r')

    # records
    for record in records:
        f.write(b' ')                        # deletion flag
        for (typ, size, deci), value in zip(fieldspecs, record):
            if typ == 'N':
                value = str(value).rjust(size, ' ')
            elif typ == 'D':
                value = value.strftime('%Y%m%d')
                if len(value) != 8:
                    value = '00000000'
            elif typ == 'L':
                value = str(value)[0].upper()
            else:
                value = str(value)[:size].ljust(size, ' ')
            assert len(value) == size
            f.write(str.encode(value))

    # End of file
    f.write(b'\x1A')

def main(argv):

    inputfile = 'properties.seq'
    outputfile = 'properties.dbf'
    csvoutputfile = 'properties.csv'

    try:
        opts, args = getopt.getopt(argv, "?hdi:o:c:", ["inputfile=",
          "outputfile=", "csvoutput="])
    except getopt.GetoptError:
        print_help()

    for opt, arg in opts:
        if opt == '-h' or opt == '-?':
            print_help()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg
        elif opt in ("-o", "--outputfile"):
            outputfile = arg
        elif opt in ("-c", "--csvoutput"):
            csvoutputfile = arg

    input = open(inputfile, "r", encoding="utf-8")
    input_reader = csv.reader(line.replace('\0', '') for line
      in input)

    row_count = 0

    header = []
    data = []

    num_columns = -1

    for row in input_reader:
        new_row = []

        for element in row:
            new_row.append(element.strip())

        num_elements = len(new_row)

        if (num_columns != -1 and num_elements != num_columns):
            if (num_elements < num_columns):
                new_row = new_row + [''] * (num_columns - num_elements)
            elif (num_elements > num_columns):
                new_row = new_row[num_columns:]

        if (row_count == 0):
            header = new_row
            num_columns = len(header)
        else:
            data.append(new_row)

        row_count = row_count + 1

    max_lens = [0] * num_columns

    for datum in data:
        x = 0

        data[x] = datum
        for element in datum:
            if (len(element) > max_lens[x]):
                max_lens[x] = len(element)
            x = x + 1


    x = 0
    fields = ''
    fields_used = []
    field_names = ''
    field_specs = []

    for field in header:
        field_same_name_count = 1
        while field in fields_used:
            field = field + str(field_same_name_count)
            field_same_name_count = field_same_name_count + 1
        fields_used.append(field)
        fields = fields + field + " C({});".format(max_lens[x]) 
        field_names = field_names + " " + field
        field_specs.append(('C', max_lens[x], 0))
        x = x + 1

    fields = fields[:-1]
    field_names = field_names[:-1]

    output = open(outputfile, "wb+")
    dbfwriter(output, fields_used, field_specs, data)
    
    output.close()

    output = open(csvoutputfile, "w", encoding="utf-8")
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(fields_used)

    for datum in data:
        writer.writerow(datum)

if __name__ == "__main__":
    main(sys.argv[1:])
