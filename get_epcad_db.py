# Copyright (c) 2014 William A Blair <wablair@awblair.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# This script fetches the zipfile containing the EPCAD tab delimitted CSV file,
# unzips it, identifies column types (integer, floating point, or string),
# creates the SQLite database and table, and then insert data into the
# database.

import StringIO
import csv
import io
import os
import re
import requests
import sqlite3
import string
import unicodedata
import zipfile

db_filename = "epcad.db"
use_file_columns = True
#url = "http://protest.epcad.org/mappingexports/database.zip"
url = "http://protest.epcad.org/mappingexports/epcad731.zip"


# Expected columns if use_file_columns is set to False.

columns = [
  'prop_id',
  'prop_val_yr',
  'geo_id',
  'zoning',
  'state_cd',
  'map_id',
  'legal_desc',
  'land_acres',
  'owner_id',
  'file_as_name',
  'addr_line2',
  'addr_city',
  'addr_state',
  'addr_zip',
  'school',
  'city',
  'college',
  'water',
  'fire',
  'emergency',
  'municipal',
  'situs_num',
  'situs_street',
  'situs_unit',
  'situs_city',
  'situs_state',
  'situs_zip',
  'exemption_list',
  'entity_list',
  'current_assessed_val',
  'current_appraised_val']

#  'previous_assessed_val',
#  'current_assessed_val',
#  'previous_appraised_val',
#  'current_appraised_val']

fp = re.compile('[-+]?[0-9]*\.?[0-9]+')

def isfloat(str):

    if fp.match(str) != None:
        return True

    return False

r = requests.get(url)

zip_file_like = io.BytesIO(r.content)

zf = zipfile.ZipFile(zip_file_like)

lands = []

# In the past the zipfile contains a directory and in that directory one tab
# delimited CSV file ending in .txt named database and then some variation on
# the date.

for info in zf.infolist():

    if ".txt" not in info.filename:
        continue

    data = zf.read(info.filename)

    # Remove the three binary characters at the start.
    # data = data[3:]

    csv_file = StringIO.StringIO(data)

    csv_reader = csv.reader(csv_file, delimiter = "\t")

    x = 0

    for row in csv_reader:

        y = 0

        for value in row:
            row[y] = filter(lambda z: z in string.printable, value.strip())
            y = y + 1

        lands.append(row)

        x = x + 1

if use_file_columns:
    columns = lands.pop(0)

max_len = 0

num_fields = len(columns)

# Try and figure out datatype of the columns.

is_digit = [True] * num_fields
is_float = [True] * num_fields
is_string = [False] * num_fields

for land in lands:

    y = 0

    for entry in land:

        try:
            entry = unicode(entry)
        except:
            print entry

        if len(entry) != 0:
            is_digit[y] = is_digit[y] and entry.isdigit()
            is_float[y] = is_float[y] and isfloat(entry)

        y = y + 1

for x in range(num_fields):
    if is_digit[x] and is_float[x]:
        is_float[x] = False
    if not (is_digit[x] or is_float[x]):
        is_string[x] = True

query = "create table if not exists epcad_data ("

x = 0

for col in columns:

    if (col[0]).isdigit():
        col = "_" + col

    query = query + col

    if is_digit[x]:
        query = query + " integer, "
    elif is_float[x]:
        query = query + " real, "
    else:
        query = query + " text, "

    x = x + 1

query = query[:-2]

query = query + ")"


# Delete old SQLite database.
try:
    os.remove(db_filename)
except:
    pass

conn = sqlite3.connect(db_filename)

c = conn.cursor()

try:
    c.execute(query)
except:
    print query

conn.commit()

x = 0

insert_query = "insert into epcad_data values (" + ("?," * num_fields)

# Remove trailing ',' and add ')'
insert_query = insert_query[:-1]
insert_query = insert_query + ")"

c.executemany(unicode(insert_query), lands)

conn.commit()

conn.close()
