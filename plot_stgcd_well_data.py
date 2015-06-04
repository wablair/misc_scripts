#!/usr/bin/env python2.7
import calendar
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pylab
import requests
import sqlite3

from datetime import date, datetime, timedelta

mpl.rcParams['lines.linewidth'] = 0.5
mpl.rcParams['lines.antialiased'] = True
mpl.rcParams['font.size'] = 10.0
mpl.rcParams['figure.figsize'] = (9, 3.5)
mpl.rcParams['figure.facecolor'] = str(0.85)
mpl.rcParams['figure.edgecolor'] = str(0.50)
mpl.rcParams['patch.linewidth'] = 0.5
mpl.rcParams['patch.facecolor'] = "348ABD"
mpl.rcParams['patch.edgecolor'] = "eeeeee"
mpl.rcParams['patch.antialiased'] = True
mpl.rcParams['axes.color_cycle'] = "348ABD, 7A68A6, A60628, 467821, " + \
    "CF4457, 188487, E24A33"

output_dir = ""

db = ""
conn = sqlite3.connect(db)

c = conn.cursor()

#now = calendar.timegm(datetime.now().utctimetuple())
#thirty_days_previous = calendar.timegm((datetime.now() - timedelta(30)).
#  utctimetuple())
#year_previous = calendar.timegm((datetime.now() - timedelta(365)).
#  utctimetuple())
now = datetime.now()
thirty_days_previous = now - timedelta(30)
year_previous = now - timedelta(365)

c.execute("select address, twdb, id from well_sites")
sites = c.fetchall()

c.execute("select site, start, slope, offset from well_variables order by " +
  "start desc")

variables = c.fetchall()

def get_variables(id, timestamp):
    for vars in variables:
        if (vars[0] == id and vars[1] <= timestamp):
            return [vars[2], vars[3]]

    return [1, 0]

def get_median_for_day(address, day):
    start = calendar.timegm(day.utctimetuple())
    end = calendar.timegm((day + timedelta(1)).utctimetuple())

    readings = list()

    for row in c.execute("select timestamp, pressure from well_readings " +
      "where address = ? and timestamp >= ? and timestamp < ?", [address, start,
      end]):
        readings.append([row[0], row[1]])

    if (len(readings) == 0):
        return [calendar.timegm(day.utctimetuple()), 0]

    mid = len(readings) / 2

    return readings[mid]

def get_first_day(address):
    for row in c.execute("select min(timestamp) from well_readings where " +
      "address = ?", [address]):
        return row[0]
    return 0

def daterange(start, end):
    for n in range(int ((end - start).days)):
        yield start + timedelta(n)

def plot_graph(times, levels, postscript):
    fig, ax = plt.subplots(1)
    ax.plot_date(times, levels, fmt = 'b-')
    fig.autofmt_xdate()
    plt.ylabel("Water Elevation\n(feet)\n\n\n", horizontalalignment = 'center')

    if len(levels) != 0:
        minimum = min(levels) - min(levels) % 5 - 10
        maximum = max(levels) - max(levels) % 5 + 10

        if (maximum < minimum):
            temp = maximum
            maximum = minimum
            minimum = maximum

        plt.ylim(minimum, maximum);

    plt.savefig(output_dir + site[1] + "_" + postscript + ".png")
    plt.close('all')

for site in sites:
    times = list()
    levels = list()

    for day in daterange(thirty_days_previous, now):
        reading = get_median_for_day(site[0], day)

        if (reading[1] > 1):
            vars = get_variables(site[2], reading[0])
            times.append(datetime.fromtimestamp(reading[0]))
            levels.append(vars[0] * reading[1] + vars[1])

    plot_graph(times, levels, "thirty_days")

    times = list()
    levels = list()

    for day in daterange(year_previous, now):
        reading = get_median_for_day(site[0], day)

        if (reading[1] > 1):
            vars = get_variables(site[2], reading[0])
            times.append(datetime.fromtimestamp(reading[0]))
            levels.append(vars[0] * reading[1] + vars[1])

    plot_graph(times, levels, "year")

    times = list()
    levels = list()

    for day in daterange(datetime.fromtimestamp(get_first_day(site[0])), now):
        reading = get_median_for_day(site[0], day)

        if (reading[1] > 1):
            vars = get_variables(site[2], reading[0])
            times.append(datetime.fromtimestamp(reading[0]))
            levels.append(vars[0] * reading[1] + vars[1])

    plot_graph(times, levels, "historical")

conn.close()
