#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A script made to "compile" TI-BASIC programs into a more efficient 
form. Supports indentation and typing without colons!

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://www.wtfpl.net/ for more details.
"""

# TODO: support writing nested items with indentation as opposed to ":THEN...:END"
# TODO: implement flag 2 "extreme"
# TODO: add more comments this code is a mess

import sys
import os
from typing import Final
import configparser
import argparse
from pathlib import Path

__author__ = "nfisherman"
__license__ = "WTFPL"
__version__ = "0.1.0"

NOTHING: Final[list] = {None, "", "\n"}
"""A list constant representing values that should be considered a blank string by the program."""

##########################
### Configuration File ###
##########################

try:
    sys.argv[1]
    sys.argv[2]
except:
    usage: str = "usage: build8xp [-h] [-o {0,1,2}] [-C DIR] input output\n"
    sys.exit(usage + "build8xp: error: the following arguments are required: input, output")

config = configparser.ConfigParser()
cfgFile = Path("default.cfg")
if not cfgFile.is_file():
    config["DEFAULT"] = {"flag": "1",
                         "directory": "./src"}
    with cfgFile.open(mode='w', encoding="utf-8") as configfile:
        config.write(configfile)
    ## END WITH ##
## END IF ##

config.read("default.cfg")

########################
### Argument Parsing ###
########################

parser = argparse.ArgumentParser(
    prog="build8xp",
    description="Compiles TI-BASIC from the form that\'s easy to write into a more efficient form")

parser.add_argument("input", type=Path, help="Sets the file to compile")
parser.add_argument("output", type=Path, help="Sets where compiled files will go")
parser.add_argument("-o", "--optimization", type=int, choices=[0, 1, 2], default=int(config["DEFAULT"]["flag"]),
    help="Sets level of optimization (0=debug, 1=normal)", dest="flag")
parser.add_argument("-C", "--directory", type=Path, default=Path(config["DEFAULT"]["directory"]),
    help="Sets the working folder", dest="dir")

args: list = parser.parse_args()
os.chdir(args.dir)

file: Path = Path(args.input)

# ensure output directory exists
Path(args.output).mkdir(parents=True, exist_ok=True)
# copy contents 
(args.output / file.name).write_bytes(file.read_bytes())

# debug flag currently does nothing (for testing)
if args.flag != 0:
    content: list
    with file.open(mode="r", encoding="utf-8") as source:
        content = source.readlines()
    ## END WITH ##
    file = args.output / file.name

    for i in range(len(content)):
        curr: str = content[i]
        if curr in NOTHING:
            continue
        ## END IF ##

        # determine if line has a newline character, if so make accomidations
        offset: int = 0
        if(curr[-1] == "\n"):
            offset = 1
        ## END IF ##
        
        # remove any indentation/extra white space, but ensure that lines are there
        curr = curr.strip() + ("\n" if offset == 1 else "")

        if i < len(content) - 2 and curr[:len(curr) - 1] in {":Then", "Then"} and content[i + 2][:len(curr) - 1] in {":End", "End"}:
            content[i] = None
            content[i + 2] = None
            continue
        ## END IF ##

        # Add colon to beginning of line if not there already
        if(curr[0] != ":"):
            curr = ":" + curr
        ## END IF ##

        # Replace all arrow placeholders ("->") with arrow character ("→")
        while curr.find("->") != -1:
            index: int = curr.find("->")
            curr = curr[:index] + "→" + curr[index + 2:]
        ## END WHILE ##

        while curr.find("\"→") != -1:
            index: int = curr.find("\"→")
            curr = curr[:index] + curr[(index + 1):]
        ## END WHILE ##

        # Replace all not equals placeholders ("<>") with not equals character ("≠")
        while curr.find("<>") != -1:
            index: int = curr.find("<>")
            curr = curr[:index] + "≠" + curr[(index + 2):]
        ## END WHILE ##

        # Remove unnecessary quotation marks and parentheses at end of line
        while curr[(-1 - offset)] == "\"" or curr[(-1 - offset)] == ")":
            curr = curr[:(len(curr) - 1 - offset)] + ("\n" if offset == 1 else "")
            # Only make new line if there was one previously ^
        ## END WHILE ##

        content[i] = curr
    ## END FOR ##

    with file.open(mode="w", encoding="utf-8") as target:
        for line in content:
            if not line in NOTHING: 
                target.write(line)
            ## END IF ##
        ## END FOR ##
    ## END WITH ##
## END IF ##