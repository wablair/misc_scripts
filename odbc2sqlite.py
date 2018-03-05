!#/usr/bin/env python3.6

import pypyodbc
import re
import sqlite3

output_db = ""

fp = re.compile('[-+]?[0-9]*\.?[0-9]+')

def isfloat(str):

    if fp.match(str) != None:
        return True

    return False

conn = pypyodbc.connect("")
cur = conn.cursor()

output_conn = sqlite3.connect(output_db)
output_cur = conn.cursor()

cur.execute("select * from sys.tables")

tables = []

for row in cur.fetchall():
    tables.append(row[0])

for table in tables:
    print(table)

    cur.execute("select * from {}".format(table))

    column_names = []

    for d in cur.description:
        column_names.append(d[0])

    x = 0

    for row in cur.fetchall():
        table_data.append(row)
        x = x + 1

    max_len = 0

    num_fields = len(column_names)

    is_digit = [True] * num_fields
    is_float = [True] * num_fields
    is_string = [False] * num_fields

    for datum in table_data:

        y = 0

        for entry in datum:

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

    query = "create table if not exists {} (".format(table)

    x = 0

    for col in column_names:

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


    try:
        output_cur.execute(query)
    except:
        print(query)

    output_conn.commit()

    x = 0

    insert_query = "insert into {} values (".format(table) + \
      ("?," * num_fields)

    # Remove trailing ',' and add ')'
    insert_query = insert_query[:-1]
    insert_query = insert_query + ")"

    output_cur.executemany(insert_query, table_data)

    output_conn.commit()

output_conn.close()
