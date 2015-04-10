import pypyodbc

conn = pypyodbc.connect('')

cur = conn.cursor()

cur.execute("select LandNumber from Land where Paid = 'N';")

lands = []

for row in cur.fetchall():
    lands.append(row[0])

for land in lands:
    sum = 0

    cur.execute('select AssessmentsLand_ID from AssessmentsLand where ' +
      'LandNumber = ?', [land])

    assessmentslands = []

    for row in cur.fetchall():
        assessmentslands.append(row[0])

    for al_id in assessmentslands:
        cur.execute('select sum(Amount) from AssessmentsFees where ' +
          'AssessmentsLand_ID = ?', [al_id])

        row = cur.fetchone()

        if row[0] != None:
            sum += row[0]

    if sum > 0:
        cur.execute("update Land set Paid = 'N' where LandNumber = ?", [land])
    else:
        cur.execute("update Land set Paid = 'Y' where LandNumber = ?", [land])
        

cur.commit()

cur.close()
conn.close()
