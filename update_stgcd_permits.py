#!/usr/bin/env python2.7

import csv
import sqlite3

conn = sqlite3.connect("default.db")
cur = conn.cursor()

input = open("stgcd_permits.csv", "r")
csv_reader = csv.DictReader(input)

cur.execute("select rowid, permit_number, permitee from permits")
permits = []

for row in cur.fetchall():
    permits.append(row)

cur.execute("select well_name, well_number, latitude, longitude, twdb, " +
    "permit_id from well_permitswells")
wells = []

for row in cur.fetchall():
    wells.append(row)

permit_info = []

for row in csv_reader:
   permit_info.append(row)

for new_permit in permit_info:
    permit_number = new_permit["permit_number"]
    permit_id = -1
    for permit in permits:
        if permit[1] == permit_number:
            permit_id = permit[0]

    if permit_id == -1:
        continue

    cur.execute("update well_permitswells set latitude = ?, longitude = ? " +
      "where permit_id = ? and well_number = ?", [new_permit["latitude"],
      new_permit["longitude"], permit_id, new_permit["well_number"]])

    if cur.rowcount == 0:
        cur.execute("insert into well_permitswells (permit_id, " +
          "well_number, well_name, twdb, latitude, longitude, notes, " +
          "aquifer_id) values (?, ?, ?, ?, ?, ?, ?, ?)", [permit_id,
          new_permit["well_number"],
          new_permit["well_name"], new_permit["twdb"], new_permit["latitude"],
          new_permit["longitude"], new_permit["note"], "217HSTN"])
        print str(new_permit["permit_number"]) + " " + \
          str(new_permit["well_number"]) + " " + new_permit["aquifer"]

conn.commit()

cur.close()
conn.close()
