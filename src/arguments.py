import argparse

def get_arguments():
    """
        Return arguments in the form as a tuple (command, extra)
    """

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-l", "--plot", help="Plot tag, scores, or happiness")
    group.add_argument("-a", "--parse", help="Rebuild database from file", action="store_true")

    args = parser.parse_args()

    if args.plot is not None:
        return ("plot", args.plot)
    elif args.parse:
        return ("parse", True)
