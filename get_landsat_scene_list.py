#!/usr/local/bin/python3.6

# Copyright (c) 2017 William A Blair <wablair@awblair.com>
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

# This script fetches the scene_list.gz from Amazon's landsat-pds and creates a
# SQLite database based off of it.


import csv
import io
import os
import re
import requests
import sqlite3
import string
import unicodedata
import gzip

db_filename = "scene_list.db"
csv_filename = "scene_list.csv"
url = " https://landsat-pds.s3.amazonaws.com/c1/L8/scene_list.gz"
output_dir = "/var/www/htdocs/landsat/"

if output_dir[-1] != "/":
    output_dir = output_dir + "/"

fp = re.compile('[-+]?[0-9]*\.?[0-9]+')

def isfloat(str):

    if fp.match(str) != None:
        return True

    return False

try:
    r = requests.get(url)
except:
    quit()

# Delete old SQLite database.
try:
    os.remove(output_dir + db_filename)
except:
    pass

# Delete old CSV file.
try:
    os.remove(output_dir + csv_filename)
except:
    pass

data = gzip.decompress(r.content)

landsats = []

csv_file = io.StringIO(data.decode("utf-8"))
csv_reader = csv.reader(csv_file, lineterminator="\n")
csv_output_file = open(output_dir + csv_filename, "w", encoding="utf-8")
csv_writer = csv.writer(csv_output_file, lineterminator="\n")

x = 0

for row in csv_reader:
    csv_writer.writerow(row)
    landsats.append(row)
    x = x + 1

columns = landsats.pop(0)

max_len = 0

num_fields = len(columns)

is_digit = [True] * num_fields
is_float = [True] * num_fields
is_string = [False] * num_fields

for landsat in landsats:

    y = 0

    for entry in landsat:

        try:
            if len(entry) != 0:
                is_digit[y] = is_digit[y] and entry.isdigit()
                is_float[y] = is_float[y] and isfloat(entry)
        except:
            print(entry)

        y = y + 1

for x in range(num_fields):
    if is_digit[x] and is_float[x]:
        is_float[x] = False
    if not (is_digit[x] or is_float[x]):
        is_string[x] = True

query = "create table if not exists scene_list ("

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


conn = sqlite3.connect(output_dir + db_filename)

c = conn.cursor()

try:
    c.execute(query)
except:
    print(query)

conn.commit()

x = 0

insert_query = "insert into scene_list values (" + ("?," * num_fields)

# Remove trailing ',' and add ')'
insert_query = insert_query[:-1]
insert_query = insert_query + ")"

c.executemany(insert_query, landsats)

conn.commit()

conn.close()
