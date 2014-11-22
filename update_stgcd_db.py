#!/usr/bin/env python2.7

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

# Update STGCD Django database with data from readings database.

import StringIO
import apsw
import io
import requests
import sqlite3

url = ""
get_db = True

if get_db:
    r = requests.get(url, stream = True)
    with open(db, "wb") as fd:
        for chunk in r.iter_content(chunk_size = 1024):
         fd.write(chunk)

input_db = ""
output_db = ""

input_conn = sqlite3.connect(input_db)
output_conn = sqlite3.connect(output_db)

i_c = input_conn.cursor()
o_c = output_conn.cursor()

i_c.execute("select address, twdb, id from sites")

sites = i_c.fetchall()

for site in sites:
    addr = site[0]

    o_c.execute("select max(timestamp) from well_readings where address = ?",
      [addr])

    row = o_c.fetchone()

    last_read = row[0]

    if (last_read == None):
        last_read = 0

    for row in i_c.execute("select timestamp, pressure, temperature from " +
      "data where address = ? and timestamp > ?", [addr, last_read]):

        o_c.execute("insert into well_readings (address, timestamp, " +
          "pressure, temperature) values (?, ?, ?, ?)", [addr, row[0], row[1],
          row[2]])

output_conn.commit()
i_c.close()
o_c.close()
input_conn.close()
output_conn.close()
