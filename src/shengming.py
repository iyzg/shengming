from collections import deque
from tinydb import TinyDB, Query
import matplotlib.pyplot as plt
import pandas as pd
import sys

import arguments
import parser

# TODO: Parse function -> send each day's text to either tags, score, happiness, etc.

def time_to_minutes(time):
    # TODO: Convert time to minutes
    split_time = time.split(":")
    return int(split_time[0]) * 60 + int(split_time[1])


# TODO: Proper way to name things and documentation
# TODO: Check for just the last week
# TODO: Write states to JSON or something then also be able to output stats from that
# TODO: Have # be comment in the file
def main():
    args = arguments.get_arguments()

    if args is None:
        print("Must pass arguments")
        sys.exit()
    
    if args[0] == "stats":
        print("todo stats")

    elif args[0] == "score":
        print("todo score")

    # Cleans out database and recreates it using life.sm
    elif args[0] == "parse":
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
            words = line.split()

            if line[0] == '#' or len(words) == 0 or not words[0][0].isdigit():
                continue
            elif "-" in words[0] and words[0][0].isdigit():
                dd['date'] = words[0].strip()
                dd['score'] = 0
                dd['tags'] = {}
                if len(words) == 3:
                    dd['happiness'] = int(words[2])
                else:
                    dd['happiness'] = 0
                lastTime = 0
                tags.clear()
                continue
            
            time_passed = time_to_minutes(words[0])
            # Process last one
            if lastTime != 0:
                dd['score'] += (time_passed - lastTime) / 15 * lastScore
                temp_tags = parser.separate_subtags(tags)

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
            tags = parser.parse_tags(line)
            lastScore = parser.parse_score(line)
    else: 
        print("Invalid command")

if __name__ == '__main__':
    main()
