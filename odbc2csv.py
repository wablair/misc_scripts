import pypyodbc
import csv

conn = pypyodbc.connect("DSN=")
cur = conn.cursor()

tables = []

cur.tables("%", "", "")
for row in cur.fetchall():
    tables.append(row[2])

for table in tables:
    cur.execute("select * from %s" % table)

    column_names = []

    for d in cur.description:
        column_names.append(d[0])

    file = open("%s.csv" % table, "w")
    writer = csv.writer(file)
    writer.writerow(column_names)

    for row in cur.fetchall():
        writer.writerow(row)

    file.close()
