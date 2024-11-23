from getopt import getopt, GetoptError
from okapi.OkAPI import OkAPI
import sys

HELP="""
okapi - API creator

Usage: okapi [OPTIONS]

-h, --help            Show this help and quit
-d, --basedir=PATH    Set different basedirectory path
"""

def main(args):

	basedir = None

	try:
		opts,rem = getopt(args, 'hd:',
				['help', 'basedir='])
	except GetoptError as ge:
		print('Error: {}'.format(ge))
		return

	for opt,arg in opts:
		if opt in ('-h', '--help'):
			print(HELP)
			return
		elif opt in ('-d', '--basedir'):
			basedir = arg


	OkAPI().run()


if __name__ == '__main__':
	main(sys.argv[1:])
