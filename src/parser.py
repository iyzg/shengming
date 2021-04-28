def parse_tags(line):
    tags = []
    for word in line.split():
        if word[0] == '@':
            tags.append(word[1:])
    return tags

def separate_subtags(tags):
    all_tags = []
    for tag in tags:
        tag_split = tag.split("(")
        for section in tag_split:
            if ')' in section:
                all_tags.append(tag_split[0] + "(" + section)
            else:
                all_tags.append(section)
    return all_tags
