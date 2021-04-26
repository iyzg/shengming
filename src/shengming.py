from tinydb import TinyDB, Query
import calplot
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import sys

import arguments
import parser

def time_to_minutes(time):
    split_time = time.split(":")
    return int(split_time[0]) * 60 + int(split_time[1])

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

        ax.plot('date', 'cnt', data=df, color="darkgrey")
        ax.plot('date', 'avg', data=df, color="black")
        ax.set_title("Plot")

        fig.autofmt_xdate()

        plt.grid(b=True, which='major', axis='y', color='ghostwhite', linestyle='-')

        plt.savefig('plot.png')

    elif args[0] == "heatmap":
        days_list = []
        cnts = []
        for day in days:
            days_list.append(day)
        days_list.reverse()

        all_days = pd.date_range(days_list[0]['date'], days_list[-1]['date'], freq='D')
        cmin = 10000
        cmax = -1
        for day in days_list:
            tcnt = 0
            if args[1] == "happiness" or args[1] == "score":
                tcnt = day[args[1]]
            elif args[1] in day['tags']:
                tcnt = day['tags'][args[1]]
            cmin = min(cmin, tcnt)
            cmax = max(cmax, tcnt)
            cnts.append(tcnt)

        events = pd.Series(cnts, index=all_days)

        calplot.calplot(events, vmin=cmin, vmax=cmax, cmap='Blues', edgecolor=None)
        plt.savefig('heatmap.png')

    # TODO: What happens if tag only in prev and not in curr, then it should be -INF
    elif args[0] == "compare":
        if args[1] == "week":
            dateOffset = datetime.timedelta(days = 7)
        elif args[1] == "month":
            dateOffset = datetime.timedelta(days = 30)
        elif args[1] == "year":
            dateOffset = datetime.timedelta(days = 365)
        else:
            print("Invalid time range")
            sys.exit()

        todayDate = datetime.datetime.now()
        prevDate = todayDate - dateOffset

        curDict = {}
        prevDict = {}

        for day in days:
            dayDate = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
            if dayDate <= prevDate - dateOffset: continue

            if prevDate < dayDate <= dayDate:
                for tag in day['tags']:
                    curDict.setdefault(tag, 0)
                    curDict[tag] += day['tags'][tag]
            elif prevDate - dateOffset < dayDate <= prevDate:
                for tag in day['tags']:
                    prevDict.setdefault(tag, 0)
                    prevDict[tag] += day['tags'][tag]

        for tag in curDict:
            if tag not in prevDict:
                change = "+INF"
                prev = 0
            else:
                prev = prevDict[tag]
                change = float(curDict[tag] - prevDict[tag]) / prevDict[tag] * 100.0
                change = str(round(change, 2))
                if change[0] != '-':
                    change = '+' + change

            
            print("{}: {}% ({} → {})".format(tag, change, prev, curDict[tag]))

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
