#!/usr/bin/env python2.7

import csv

new_file = open("hcuwcd_new_permits.csv", "r")
new_reader = csv.DictReader(new_file)

old_file = open("hcuwcd_old_permits.csv", "r")
old_reader = csv.DictReader(old_file)

out_file = open("hcuwcd_permit_changes.csv", "w")
out_writer = csv.writer(out_file)

new_permits = []
old_permits = []

for row in new_reader:
    new_permits.append(row)

new_new_permits = []

for permit in new_permits:

    for x in range(1, 13):

        if not permit["Lat" + str(x)] or not permit["Lon" + str(x)]:
            continue

        lat = permit["Lat" + str(x)].replace("N", "")
        lat = lat.split(' ')
        lat = float(lat[0]) + float(lat[1]) / 60.0
        lat = float("{:.6f}".format(lat))

        lon = permit["Lon" + str(x)].replace("W", "")
        lon = lon.split(' ')
        lon = -(float(lon[0]) + float(lon[1]) / 60.0)
        lon = float("{:.6f}".format(lon))

        new_new_permits.append([permit["New Permit"], x, lat, lon, False])

for row in old_reader:
    old_permits.append(row)

new_permits = new_new_permits

temp_permits = []

for permit in old_permits:
    permit_name = permit["Temp. Permit"].split("_")
    old_permit_name = permit["Old Permit"].split("_")
    if not "_" in permit["Old Permit"]: 
        old_permit_name.append("");
    temp_permits.append([permit_name[0], permit_name[1], float(permit["Lat"]),
      float(permit["Long"]), False, old_permit_name[0], old_permit_name[1],
      permit["Meter SN"]])

out_writer.writerow(["New Permit", "New Well Number", "Temp Permit",
  "Temp Well Number", "Old Permit", "Old Well Number", "Lat", "Lon", "SN"])

for new in new_permits:

    for temp in temp_permits:

        if new[2] == temp[2] and new[3] == temp[3] and not temp[4] and \
          not new[4]:
            temp[4] = True
            new[4] = True
            out_writer.writerow([new[0], new[1], temp[0],
              temp[1], temp[5], temp[6], temp[2], temp[3], temp[7]])

out_writer.writerow(["Not used"])

for new in new_permits:
    if not new[4]:
        out_writer.writerow([new[0],new[1], "", "", "", "", new[2], new[3]])

for temp in temp_permits:
    if not temp[4]:
        out_writer.writerow(["", "", temp[0], temp[1], temp[5], temp[6],
          temp[2], temp[3], temp[7]])

print len(new_permits)
