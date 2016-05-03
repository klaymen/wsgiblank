"""
simple script to parse the python-style config file

"""

import ConfigParser
import sys, os


def usage():
    print """./%s <configFile> <group> <key>""" % ( sys.argv[0] )
    sys.exit()

if len(sys.argv) < 4 or sys.argv[1].lower() in ('-h', '--help', ):
    usage()
    sys.exit(-2)

try:
    config = ConfigParser.ConfigParser()
    config.read( sys.argv[1] )
except:
    sys.exit(-1)

try:
    print config.get( sys.argv[2], sys.argv[3] ),
except:
    sys.exit(-1)

