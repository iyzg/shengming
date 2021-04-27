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

# TODO: Get rid of FIN for all 24d hrs. and ending on next day
# TODO: ^ Remember if last line and you have a day not processed, add it
def main():
    args = arguments.get_arguments()

    if args is None:
        print("Must pass arguments")
        sys.exit()
    
    db = TinyDB('db.json')
    days = db.table('days')

    if args[0] == "plot":
        gp = {'cnt':[], 'date':[]}
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

        df = pd.DataFrame(gp)
        df.set_index('date', inplace=True)
        
        df['avg'] = df.cnt.ewm(alpha=0.2, adjust=False).mean()

        fig, ax = plt.subplots()
        colors = ['darkgrey', 'black']
        df[['cnt', 'avg']].plot(color=colors, linewidth=1, figsize=(12,6), ax=ax)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

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

        spec_args = args[1].split()
        area = spec_args[0]
        if len(spec_args) == 2:
            color = spec_args[1]
        else:
            color = "Blues"

        for day in days_list:
            tcnt = 0
            if area == "happiness" or area == "score":
                tcnt = day[area]
            elif area in day['tags']:
                tcnt = day['tags'][area]
            cmin = min(cmin, tcnt)
            cmax = max(cmax, tcnt)
            cnts.append(tcnt)

        events = pd.Series(cnts, index=all_days)

        calplot.calplot(events, vmin=cmin, vmax=cmax, cmap=color, edgecolor=None)
        plt.savefig('heatmap.png')

    # TODO: What happens if tag only in prev and not in curr, then it should be -INF
    elif args[0] == "compare":
        if args[1] == "week":
            dateoffset = datetime.timedelta(days = 7)
        elif args[1] == "month":
            dateoffset = datetime.timedelta(days = 30)
        elif args[1] == "year":
            dateoffset = datetime.timedelta(days = 365)
        else:
            print("invalid time range")
            sys.exit()

        todaydate = datetime.datetime.now()
        prevdate = todaydate - dateoffset

        curdict = {}
        prevdict = {}

        for day in days:
            daydate = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
            if daydate <= prevdate - dateoffset: continue

            if prevdate < daydate <= daydate:
                for tag in day['tags']:
                    curdict.setdefault(tag, 0)
                    curdict[tag] += day['tags'][tag]
            elif prevdate - dateoffset < daydate <= prevdate:
                for tag in day['tags']:
                    prevdict.setdefault(tag, 0)
                    prevdict[tag] += day['tags'][tag]

        for tag in curdict:
            if tag not in prevdict:
                change = "+inf"
                prev = 0
            else:
                prev = prevdict[tag]
                change = float(curdict[tag] - prevdict[tag]) / prevdict[tag] * 100.0
                change = str(round(change, 2))
                if change[0] != '-':
                    change = '+' + change

            
            print("{}: {}% ({} → {})".format(tag, change, prev, curdict[tag]))

    elif args[0] == "pie":
        if args[1] == "week":
            dateoffset = datetime.timedelta(days = 7)
        elif args[1] == "month":
            dateoffset = datetime.timedelta(days = 30)
        elif args[1] == "year":
            dateoffset = datetime.timedelta(days = 365)
        else:
            print("invalid time range")
            sys.exit()

        todaydate = datetime.datetime.now()
        prevdate = todaydate - dateoffset

        dct = {}

        for day in days:
            daydate = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
            if prevdate < daydate <= todaydate:
                for tag in day['tags']:
                    dct.setdefault(tag, 0)
                    dct[tag] += day['tags'][tag]

        labels = []
        times = []
        for k, v in dct.items():
            if '(' in k:
                continue
            labels.append(k)
            times.append(v)

        plt.pie(times, labels=labels, autopct='%1.1f%%')

        plt.axis('equal')
        plt.savefig('pie.png')

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
                if dd:
                    time_passed = time_to_minutes("24:00")
                    dd['score'] += (time_passed - lastTime) / 15 * lastScore
                    temp_tags = parser.separate_subtags(tags)

                    for ttag in temp_tags:
                        dd['tags'].setdefault(ttag, 0)
                        dd['tags'][ttag] += time_passed - lastTime
                    days.insert(dd)
                    dd.clear()

                dd['date'] = words[0].strip()
                dd['score'] = 0
                dd['tags'] = {}
                if len(words) == 3:
                    dd['happiness'] = int(words[2])
                else:
                    dd['happiness'] = 0
                lastTime = -1
                tags.clear()
                continue
            
            time_passed = time_to_minutes(words[0])
            # Process last one
            if lastTime != -1:
                dd['score'] += (time_passed - lastTime) / 15 * lastScore
                temp_tags = parser.separate_subtags(tags)

                for ttag in temp_tags:
                    dd['tags'].setdefault(ttag, 0)
                    dd['tags'][ttag] += time_passed - lastTime

            # Push Current (Not if FIN)
            tags.clear()

            lastTime = time_passed
            tags = parser.parse_tags(line)
            lastScore = parser.parse_score(line)

        if dd:
            days.insert(dd)
    else: 
        print("Invalid command")

if __name__ == '__main__':
    main()
