import os
import pypyodbc
import re
import sqlite3

output_db = ".db"

fp = re.compile('^[-+]?[0-9]*\.?[0-9]+$')

def isfloat(str):

    if fp.match(str) != None:
        return True

    return False

try:
    os.remove(output_db)
except:
    print("Could not delete db.")

conn = pypyodbc.connect("")
cur = conn.cursor()

output_conn = sqlite3.connect(output_db)
output_cur = output_conn.cursor()

cur.execute("select * from sys.tables")

tables = []

for row in cur.fetchall():
    tables.append(row[0])

tables = ['owners', 'canals', 'orders', 'crops', 'ordersdetailcrops']

for table in tables:
    cur.execute("select * from {}".format(table))

    column_names = []

    for d in cur.description:
        column_names.append(d[0])

    num_fields = len(column_names)

    is_digit = [True] * num_fields
    is_float = [True] * num_fields
    is_string = [False] * num_fields

    x = 0

    table_data = []

    for row in cur.fetchall():
        temp_row = []

        y = 0

        for entry in row:
            str_entry = str(entry)
            if str_entry == 'None':
                str_entry = ''

            if len(str_entry) != 0:
                is_digit[y] = is_digit[y] and str_entry.isdigit()
                is_float[y] = is_float[y] and isfloat(str_entry)

            temp_row.append(str_entry)

            y = y + 1

        table_data.append(temp_row)

        x = x + 1

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

    for datum in table_data:
        try:
            output_cur.execute(insert_query, datum)
        except:
            print(query)

    output_conn.commit()

output_conn.close()
