#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#Script that converts umatrix rules from a minimal state to a maximal and vice versa
#
#License: GPL-3.0


from collections import defaultdict
import operator
import sys
import os
import re

if len(sys.argv)>1:
    if sys.argv[1]!="":
        if os.path.isfile(sys.argv[1]):
            input_filename=sys.argv[1]
        else:
            print("invalid input filename")
            exit()
    else:
        print("please specify input file")
        exit()
else:
    print("please specify input file")
    exit()

if len(sys.argv)>2:
    if sys.argv[2] != "":
        if sys.argv[2] == "min2max" or sys.argv[2]=="max2min":
            mode = sys.argv[2]
        else:
            print ("invalid mode. only min2max and max2min allowed")
            exit()
    else:
        mode = "min2max"
else:
    mode = "min2max"

if len(sys.argv)>3:
    if sys.argv[3] != "":
        if os.path.isfile(sys.argv[1]):
            output_filename=sys.argv[1]
        else:
            print("invalid output file")
            exit()
    else:
        output_filename = "output.txt"
else:
    output_filename = "output.txt"

#open umatrix rule set file
with open(input_filename) as f:
    lines = f.readlines()

#open umatrix directives
with open("directives.txt") as f:
    directives = f.readlines()

directives = [directive.strip() for directive in directives]

print("converting from "+mode)

filters=[]
scopes=defaultdict()
requests=["cookie","css","image","script","plugin","frame","media","xhr","other","doc","*"]

for line in lines:
    if line.strip()=="":
        filters += [line]
        print("empty line: " + line)
    elif line.strip()[0]=="#":
        print("comment: " + line)
        filters+=[line]
    elif line.strip().split(":")[0] in directives:
        print("drirective: " + line)
        filters+=[line]
    else:
        rule = re.search(r'([a-zA-Z\d-]+(?:\.[a-zA-Z\d-]+)*|\*)\s+([a-zA-Z\d-]+(?:\.[a-zA-Z\d-]+)*|\*|1st-party)\s+(cookie|css|image|doc|script|plugin|frame|media|xhr|other|\*)\s+(block|allow|inherit|\*)\s*', line)
        if rule:
            #print("filter rule: "+rule.group() )

            if not rule.group(1) in scopes:
                scopes[rule.group(1)]={}
            if not rule.group(2) in scopes[rule.group(1)]:
                scopes[rule.group(1)][rule.group(2)]={}
            if not rule.group(3) in scopes[rule.group(1)][rule.group(2)]:
                scopes[rule.group(1)][rule.group(2)][rule.group(3)]={}
            if rule.group(4)=="allow":
                scopes[rule.group(1)][rule.group(2)][rule.group(3)]= True
            elif rule.group(4)=="block":
                scopes[rule.group(1)][rule.group(2)][rule.group(3)] = False
            else:
                print("ignored rule: " + line)
                filters += [line]
        else:
                print("invalid rule: "+line)
                filters += [line]

#evaluating priorities
#
#iterating over each destination for each scope and over each umatrix request type (every cell in the matrix for every website)
#this includes the * entries
#value is the allow/block state of the current cell
#then start with the most general rule and then override with every more specific rule

for scope, s in scopes.items():
    for destination, d in s.items():
        for request in requests:
            print(scope+" "+destination+" "+request)

            if "*" in scopes:
                if "*" in scopes["*"]:
                    if "*" in scopes["*"]["*"]:
                        if scopes["*"]["*"]["*"]==True:
                            value=True
                        else:
                            value=False
                    if request in scopes["*"]["*"]:
                        if scopes["*"]["*"][request]==True:
                            value=True
                        else:
                            value=False

                if destination in scopes["*"]:
                    if "*" in scopes["*"][destination]:
                        if scopes["*"][destination]["*"]==True:
                            value=True
                        else:
                            value=False
                    if request in scopes["*"][destination]:
                        if scopes["*"][destination][request]==True:
                            value=True
                        else:
                            value=False

            if scope in scopes:
                if "*" in scopes[scope]:
                    if "*" in scopes[scope]["*"]:
                        if scopes[scope]["*"]["*"]==True:
                            value = True
                        else:
                            value = False
                    if request in scopes[scope]["*"]:
                        if scopes[scope]["*"][request]==True:
                            value = True
                        else:
                            value = False
                if destination in scopes[scope]:
                    if "*" in scopes[scope][destination]:
                        if scopes[scope][destination]["*"]==True:
                            value = True
                        else:
                            value = False
                    if request in scopes[scope][destination]:
                        if scopes[scope][destination][request]==True:
                            value = True
                        else:
                            value = False
            if value:
                filters += [scope + " " + destination + " " + request + " " + "allow"]
            else:
                filters += [scope + " " + destination + " " + request + " " + "block"]


#write list to disk
print("writing to disk")
outfile = open(output_filename, 'w')

for line in filters:
  outfile.write("%s\n" % line)
outfile.close()
