from ...vendor.SplashPyUtils import logger

import sys

def print_help():
    logger.log.print("SourceStream Manual", "\n\n");

    logger.log.print("Usage: 'python3 " + sys.argv[0] + " <argument 1> [argument 2]'");
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
        "help                                             :  Prints out the manual.", ["h", "man", "manual"],
        "serv                                             :  Running SourceStream as a service.",
        "package:<name>:[version]                         :  Select a specific package to pack.", ["p:<name>:[ver]"],
        "package-list:[package]:[version]                 :  List out all packages required by the edition.", ["list"],
        "upstream-add:<name>:[url]:[version]:[checksum]   :  Adding new source to the upstream-sources.yml(will lock yaml file)",
        "upstream-modify:<name/url>:<new value>           :  Modify existing source(will lock yaml file)",
        "upstream-checksum:<name>:<version>:<checksum>    :  Update or add checksum for spesific version(will lock yaml file)",
        "upstream-remove:<name>                           :  Removes existing source(will lock yaml file)",

    ]

    logger.log.tree(help_available_args, False);
    exit()