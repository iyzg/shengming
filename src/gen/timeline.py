import sqlite3

con = sqlite3.connect('lei.db')
cur = con.cursor()

q = cur.execute('SELECT division.name AS title, log.date, log.time AS hours FROM log INNER JOIN division ON division.rowid = log.division_id ORDER BY log.rowid ASC')
        #  , log.time AS hours FROM log JOIN division ON division.rowid = log.division_id ORDER BY ASC')

desiredDays = 8

rows = []
for row in q:
    rows.append([row[1], row[0], row[2]])

days = [None] * desiredDays
day = []
now = rows[0][0]

for i in range(len(rows)):
    if now != rows[i][0]:
        now = rows[i][0]

        days[desiredDays - 1] = day
        desiredDays -= 1
        day = []

    day.append([rows[i][1], rows[i][2]])

# TODO: Change so that it feels in the appropriate day
days[0] = day

total = {}
maxHours = 0

for day in days:
    print(day)

for i in range(len(days)):
    hours = 0

    if days[i] == None: 
        continue

    for j in range(len(days[i])):
        hours += days[i][j][1]

    if hours > maxHours:
        maxHours = hours

if maxHours == 0:
    maxHours = 1

