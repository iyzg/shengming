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
    
    db = TinyDB('db.json')
    days = db.table('days')

    if args[0] == "plot":
        gp = {'cnt':[], 'date':[], 'avg':[]}
        queue = []
        total = 0
        days_list = []
        for day in days:
            days_list.append(day)
        days_list.reverse()

        for day in days_list:
            tcnt = 0
            if args[1] == "happiness" or args[1] == "score":
                tcnt = day[args[1]]
            elif args[1] in day['tags']:
                tcnt = day['tags'][args[1]]

            gp['cnt'].append(tcnt)
            gp['date'].append(day['date'])
            total += tcnt
            queue.append(tcnt)
            if len(queue) == 8:
                total -= queue.pop(0)
            gp['avg'].append(total / len(queue))

        df = pd.DataFrame(gp)

        fig, ax = plt.subplots()

        ax.plot('date', 'cnt', data=df, color="gainsboro")
        ax.plot('date', 'avg', data=df, color="black")
        ax.set_title("Plot")

        fig.autofmt_xdate()

        plt.savefig('plot.png')

    # Cleans out database and recreates it using life.sm
    elif args[0] == "parse":
        log = None
        tags = []

        lastScore = 0
        lastTime = 0

        # TODO: Different tables for days/tags/etc.
        # Clean out past database
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
