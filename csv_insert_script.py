#!/usr/bin/env python2.7

import csv
import sqlite3

conn = sqlite3.connect("twdb.db")
cur = conn.cursor()

file = open('stgcd_manual.csv', 'r')

reader = csv.reader(file)

readings = []
twdb_nums = []

for row in reader:
    readings.append(row)
    if (row[0] not in twdb_nums):
        twdb_nums.append(row[0])

readings.pop(0)
twdb_nums.pop(0)

for twdb in twdb_nums:
    cur.execute("select owner_1, owner_2 from twdb_weldta where " +
      "state_well_number = ?", [twdb])
    row = cur.fetchone()
    print ("insert into well_sites_manual (twdb, name) values (" + str(twdb) +
      ", '" + str(str(row[0]) + " " + str(row[1])).strip() + "');")

for reading in readings:
    print("insert into well_readings_manual (twdb_id, date, depth_to_water) " +
	  "values (" + str(reading[0]) + ", '" + str(reading[1]) + "', " +
      str(reading[2]) + ");")
