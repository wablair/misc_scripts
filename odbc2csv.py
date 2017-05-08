import pypyodbc
import csv

conn = pypyodbc.connect("DSN=HOSS_DB")
cur = conn.cursor()

cur.execute("select * from sys.tables")

for row in cur.fetchall():
    tables.append(row[0])

tables = ["land"]

for table in tables:
    print(table)

    cur.execute("select * from {}".format(table))

    column_names = []

    for d in cur.description:
        column_names.append(d[0])

    file = open("{}.csv".format(table), "w", encoding="utf-8")
    writer = csv.writer(file, lineterminator='\n')
    writer.writerow(column_names)

    for row in cur.fetchall():
        writer.writerow(row)

    file.close()
