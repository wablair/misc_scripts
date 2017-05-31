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

# Get TIFFs for recent Landsat based on row, path, and bands.
# Needs SQLite3 databse generated by get_landsat_scene_list.py.

import io
import os
import re
import requests
import sqlite3
import string

path = 32
row = 38
bands = [4, 5, 8]
max_cloud = 10

db_filename = "/var/www/htdocs/landsat/scene_list.db"
output_dir = "/var/www/htdocs/landsat/"

if output_dir[-1] != "/":
    output_dir = output_dir + "/"

conn = sqlite3.connect(db_filename)

c = conn.cursor()
query = ("select productId, cloudCover, download_url from scene_list where " +
  "path = {} and row = {} and productId like '%_T1' and cloudCover <= {} " +
  "order by productId desc limit 1").format(path, row, max_cloud)

try:
    c.execute(query)
except:
    print(query)
    conn.close()
    quit()

row = c.fetchone()

if (row == None):
    conn.close()
    quit()

url = row[2].replace("index.html", "")

for band in bands:
    filename = row[0] + ("_B{}").format(band) + ".TIF"
    tiff_url = url + filename
    output = output_dir + filename
    if os.path.isfile(output):
        continue
    print(("Getting {}").format(tiff_url))
    r = requests.get(tiff_url, stream=True)
    r.raise_for_status()
    with open(output, 'wb') as handle:
        for block in r.iter_content(1024):
            handle.write(block)

conn.close()
