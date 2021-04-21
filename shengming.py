from collections import deque
from tinydb import TinyDB, Query
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import sys
import datetime

# TODO: Parse function -> send each day's text to either tags, score, happiness, etc.


def score():
    db = TinyDB('db.json')
    days_table = db.table('days')
    gp = {'score':[], 'date':[], 'avg':[]}
    queue = deque([])
    total = 0
    days = []
    for day in days_table:
        days.append(day)
    days.reverse()

    for day in days:
        gp['score'].append(day['score'])
        gp['date'].append(day['date'])
        total += day['score'] 
        queue.append(day['score'])
        if len(queue) == 8:
            total -= queue.popleft()
        gp['avg'].append(total / len(queue))

    df = pd.DataFrame(gp)

    fig, ax = plt.subplots()

    ax.plot('date', 'score', data=df, color="gainsboro")
    ax.plot('date', 'avg', data=df, color="black")
    ax.set_title("Daily Scores")

    fig.autofmt_xdate()

    plt.savefig('score_plot.png')

def graph(tag):
    db = TinyDB('db.json')
    days_table = db.table('days')
    gp = {'time':[], 'date':[], 'avg':[]}
    queue = deque([])
    total = 0
    days = []
    for day in days_table:
        days.append(day)
    days.reverse()

    for day in days:
        tt = 0
        if tag in day['tags']:
            tt = day['tags'][tag]
        gp['time'].append(tt)
        gp['date'].append(day['date'])
        total += tt
        queue.append(tt)
        if len(queue) == 8:
            total -= queue.popleft()
        gp['avg'].append(total / len(queue))

    df = pd.DataFrame(gp)

    fig, ax = plt.subplots()

    ax.plot('date', 'time', data=df, color="gainsboro")
    ax.plot('date', 'avg', data=df, color="black")
    ax.set_title("Time spent on @{}".format(tag))

    fig.autofmt_xdate()

    plt.savefig('plot.png')

def parse():
    # TODO: Add way for scores / 30 minutes
    # TODO: Happiness every day
    log = None
    tags = []

    lastScore = 0
    lastTime = 0

    # TODO: Different tables for days/tags/etc.
    db = TinyDB('db.json')
    days = db.table('days')
    days.truncate()

    try:
        log = open("life.sm", "r")
    except IOError:
        print("No daily file found")
        sys.exit()

    lines = log.readlines()
    dd = {}
    for line in lines:
        if line[0] == '#':
            continue

        words = line.split()

        # TODO: Handle subtag
        # Reset when you're on dates
        if len(words) == 0:
            continue
        elif "-" in words[0] and words[0][0].isdigit():
            dd['date'] = words[0].strip()
            dd['score'] = 0
            dd['tags'] = {}
            lastTime = 0
            tags.clear()
            continue

        if not words[0][0].isdigit():
            continue

        time_passed = time_to_minutes(words[0])
        # Process last one
        if lastTime != 0:
            dd['score'] += (time_passed - lastTime) / 15 * lastScore
            for tag in tags:
                temp_tags = []
                tag_split = tag.split("(")
                for section in tag_split:
                    if ')' in section:
                        temp_tags.append(tag_split[0] + "(" + section)
                    else:
                        temp_tags.append(section)

                for ttag in temp_tags:
                    dd['tags'].setdefault(ttag, 0)
                    dd['tags'][ttag] += time_passed - lastTime

        # Push Current (Not if FIN)
        tags.clear()
        if words[1] == "FIN":
            days.insert(dd)
            dd.clear()
            continue

        lastTime = time_passed
        lastScore = 0
        for word in words:
            if word[0] == '@':
                tags.append(word[1:])
            elif word[0] == '-':
                lastScore = int(word)
            elif word[0] == '+':
                lastScore = int(word[1:])

def paper_parse():
    # Manually create a list of tags
    tags = ["exercise", "social", "research", "leisure", "school", "maintenance", "happiness"]

    day = {}

    # Store date (month/day/year) in the date key.
    date = datetime.datetime.now()
    day["date"] = date.strftime("%Y-%m-%d")

    # Prompt user for hours spent on each tag and store it in the tag key in minutes.
    for tag in tags:
        if tag == "happiness":
            day[tag] = float(input(tag + ": "))
        else:
            day[tag] = float(input(tag + ": ")) * 60

    db = TinyDB('db.json')
    days = db.table('days')
    days.insert(day)
    print("Hours stored.")

def time_to_minutes(time):
    # TODO: Convert time to minutes
    split_time = time.split(":")
    return int(split_time[0]) * 60 + int(split_time[1])


# TODO: Proper way to name things and documentation
# TODO: Check for just the last week
# TODO: Score for every day
# TODO: Write states to JSON or something then also be able to output stats from that
# TODO: Have # be comment in the file
def main():
    # Arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-u", "--update", help="Update database")
    group.add_argument("-s", "--stats", metavar="tag", help="Get stats for tag")
    group.add_argument("-c", "--score", help="Get stats for tag")
    group.add_argument("-p", "--paper", action="store_true", help="Input hours per tag instead of schedule")

    args = parser.parse_args()

    if args.stats != None:
        graph(args.stats)
        sys.exit()

    if args.score != None:
        score()
        sys.exit()

    if args.paper:
        paper_parse()
    else:
        parse()



if __name__ == '__main__':
    main()
