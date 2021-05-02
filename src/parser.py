import csv
import sqlite3

# table arrays
tasks = []
projects = []
divisions = []
logs = []

source = open("prd.csv", "r")
con = sqlite3.connect('prd.db')
cur = con.cursor()

# for each line in source
count = 0

for row in source:
	count += 1

	if count == 1:
		continue

	# deconstruct log and clean up
	string = row.split(",", 5)

	date = string[0]
	time = string[1]
	project = string[2].replace("'", "\\'").replace('"', '\\"').strip()
	task = string[3].replace("'", "\\'").replace('"', '\\"').strip()
	division = string[4].replace("'", "\\'").replace('"', '\\"').strip()
	details = string[5].replace("'", "\\'").replace('"', '').replace('\n', ' ').replace('\r', '').strip()

	# if project / task / division is not yet noted, add to respective table array
	if not project in projects:
		projects.append(project)

	if not task in tasks:
		tasks.append(task)

	if not division in divisions:
		divisions.append(division)

	# add log
	logs.append([date, time, project, task, division, details])

cur.execute("DROP TABLE IF EXISTS log;")
cur.execute("DROP TABLE IF EXISTS project;")
cur.execute("DROP TABLE IF EXISTS task;")
cur.execute("DROP TABLE IF EXISTS division;")

cur.execute('''
CREATE TABLE IF NOT EXISTS log (
    date TEXT, 
    time INTEGER,
    project_id TEXT,
    task_id TEXT,
    division_id TEXT,
    details TEXT
);''')

cur.execute('''
CREATE TABLE IF NOT EXISTS division (
    name TEXT
);''')

cur.execute('''
CREATE TABLE IF NOT EXISTS project (
    name TEXT
);''')

cur.execute('''
CREATE TABLE IF NOT EXISTS task (
    name TEXT
);''')

for division in divisions:
    cur.execute("INSERT INTO division VALUES (?)", (division,))

for task in tasks:
    cur.execute("INSERT INTO task VALUES (?)", (task,))

for project in projects:
    cur.execute("INSERT INTO project VALUES (?)", (project,))

for log in logs:
    cur.execute('''
    INSERT INTO log (date, time, project_id, task_id, division_id, details)
    VALUES(?,
    ?,
    (SELECT rowid FROM project WHERE name = ?),
    (SELECT rowid FROM task WHERE name = ?),
    (SELECT rowid FROM division WHERE name = ?),
    ?)''', (log[0], log[1], log[2], log[3], log[4], log[5]))

con.commit()
con.close()
