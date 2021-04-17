import sys
from tinydb import TinyDB, Query

# TODO: Parse function -> send each day's text to either tags, score, happiness, etc.

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
        sys.exit();

    lines = log.readlines()

    dd = {}
    for line in lines:
        if line[0] == '#':
            continue

        words = line.split()

        # TODO: Handle subtag
        # Reset when you're on dates
        if len(words) == 0:
            continue;
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
                    dd['tags'][ttag] = time_passed - lastTime
                    if ttag not in tagTime:
                        tagTime[ttag] = time_passed - lastTime
                    else:
                        tagTime[ttag] += time_passed - lastTime

        # Push Current (Not if FIN)
        tags.clear()
        if words[1] == "FIN":
            print(dd)
            days.insert(dd) 
            dd.clear()
            continue

        lastTime = time_passed
        for word in words:
            if word[0] == '@':
                tags.append(word[1:])

    for tag in sorted(tagTime):
        if "(" not in tag:
            print()
        print("{}: {} minutes".format(tag, tagTime[tag]))

    days.all()

if __name__ == '__main__':
    main()
