from collections import deque
from tinydb import TinyDB, Query
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

# TODO: Parse function -> send each day's text to either tags, score, happiness, etc.

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

    ax.plot('date', 'time', data=df)
    ax.plot('date', 'avg', data=df)
    ax.set_title("Time spent on @{}".format(tag))

    fig.autofmt_xdate()

    plt.savefig('plot.png')

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

    args = parser.parse_args()

    if args.stats != None:
        graph(args.stats)
        sys.exit()



    # TODO: Add way for scores / 30 minutes
    # TODO: Happiness every day
    log = None
    tags = []
    tagTime = {}

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
            dd['tags'] = {}
            lastTime = 0
            tags.clear()
            continue

        if not words[0][0].isdigit():
            continue

        
        time_passed = time_to_minutes(words[0])
        # Process last one
        if lastTime != 0:
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

                    if ttag not in tagTime:
                        tagTime[ttag] = time_passed - lastTime
                    else:
                        tagTime[ttag] += time_passed - lastTime

        # Push Current (Not if FIN)
        tags.clear()
        if words[1] == "FIN":
            days.insert(dd) 
            dd.clear()
            continue

        lastTime = time_passed
        for word in words:
            if word[0] == '@':
                tags.append(word[1:])

if __name__ == '__main__':
    main()
