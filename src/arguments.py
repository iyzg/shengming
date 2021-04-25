import argparse

def get_arguments():
    """
        Return arguments in the form as a tuple (command, extra)
    """

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-a", "--parse", help="Rebuild database from file", action="store_true")
    group.add_argument("-c", "--compare", help="Compare stats from last 2 {week, month, year}")
    group.add_argument("-e", "--heatmap", help="Heatmap tag, scores, or happiness")
    group.add_argument("-l", "--plot", help="Plot tag, scores, or happiness")

    args = parser.parse_args()

    if args.plot is not None:
        return ("plot", args.plot)
    elif args.heatmap is not None:
        return ("heatmap", args.heatmap)
    elif args.compare is not None:
        return ("compare", args.compare)
    elif args.parse:
        return ("parse", True)
