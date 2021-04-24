import argparse

def get_arguments():
    """
        Return arguments in the form as a tuple (command, extra)
    """

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-t", "--stats", help="Get stats for tags")
    group.add_argument("-c", "--score", help="Get graph of score", action="store_true")
    group.add_argument("-p", "--parse", help="Rebuild database from file", action="store_true")

    args = parser.parse_args()

    if args.stats is not None:
        return ("stats", args.stats)
    elif args.score:
        return ("score", True)
    elif args.parse:
        return ("parse", True)
