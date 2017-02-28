import datetime
import pypyodbc
import re
import struct

import mysql.connector
from mysql.connector import errorcode


multi_db = False

mysql_host = ""
mysql_user = ""
mysql_password = ""
mysql_db = ""

config = {
    'user': mysql_user,
    'password': mysql_password,
    'host': mysql_host,
    'database': mysql_db
}

def dbfwriter(f, fieldnames, fieldspecs, records):
    """
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
            elif typ == 'L':
                value = str(value)[0].upper()
            else:
                value = str(value)[:size].ljust(size, ' ')
            try:
                assert len(value) == size
            except:
                print(value)
                print(len(value))
                print(size) 
                continue
            f.write(str.encode(value))

    # End of file
    f.write(b'\x1A')


meters = {}
sites = {}
categories = {}

mysql_conn = mysql.connector.connect(**config)
mysql_cur = mysql_conn.cursor()

mysql_cur.execute("select id, path, expression, site from meter " +
  "where in_use = true")

for row in mysql_cur.fetchall():
    if (row[3] in meters):
        meters[row[3]].append([row[0], row[1], row[2]])
    else:
        meters[row[3]] = [[row[0], row[1], row[2]]]

mysql_cur.execute("select id, category from site")

for row in mysql_cur.fetchall():
    if (row[1] in sites):
        sites[row[1]].append(row[0])
    else:
        sites[row[1]] = [row[0]]

mysql_cur.execute("select id, db, process, server from category")

for row in mysql_cur.fetchall():
    categories[row[0]] = [row[1], row[2], row[3]]

mysql_cur.close()
mysql_conn.close()

if not multi_db:
    conn = pypyodbc.connect("DSN=")
    cur = conn.cursor()

for id, category in categories.items():
    if multi_db:
        conn = pypyodbc.connect("DSN=" + category[0])
        cur = conn.cursor()


    site_list = sites[id]


    sources = []
    for site in site_list:
        try:
            meter_list = meters[site]
        except:
            continue
        
        for meter in meter_list:
            ''' server/process/path/expression '''
            src = category[2] + "/" + category[1] + "/" + meter[1] + "/" + \
              meter[2]
            sources.append([src, meter[1], meter[2]])

    records = []

    for src in sources:
        query = "select top 1 LocalTime, \"" + src[0] + "\" from " + \
            "NICIT.RawData order by LocalTime desc;"

        try:
            cur.execute(query)
        except:
            continue

        try:
            row = cur.fetchone()
        except:
            continue

        value = 0

        if (row[1]):
            value = round(row[1], 2)

        modbus = int((re.findall(r'\d+', src[1]))[0])

        if (value != 0):
            records.append([modbus, src[2], row[0], value])

    try:
        output = open(category[1] + ".dbf", "wb")
    except:
        continue

    dbfwriter(output, ['site', 'expression', 'date', 'value'],
      [["N", 3, 0], ["C", 12, 0],  ["D", 8, 0], ["N", 12, 2]], records)
