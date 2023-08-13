from ...vendor.SplashPyUtils import logger

import sys

def print_help():
    logger.log.print("SourceStream Manual", "\n\n");

    logger.log.print("Usage: 'python3 " + sys.argv[0] + " --<argument 1> --[argument 2]'");
    logger.log.print("<> = required argument")
    logger.log.print("[] = optional argument", "\n\n")

    logger.log.print("Help tree format:");
    help_explain_tree = [
        "argument 1",
        "argument 2", ["alternative for argument 2"],
        "argument 3"

    ]
    logger.log.tree(help_explain_tree, False);

    logger.log.print("", "\n\n");

    logger.log.print("Available arguments:")
    help_available_args = [
        "help                      :    Prints out the manual.", ["h", "man", "manual"],
        "list-packages             :    List out all packages required by the edition.", ["list"],
        "package:<name>:[version]  :    Select a specific package to pack.", ["p:<name>:[ver]"],

    ]

    logger.log.tree(help_available_args, False);
    exit()