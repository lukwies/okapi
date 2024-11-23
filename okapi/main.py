"""
Okapi - A tool for API development
Copyright (C) 2024 Lukas Wiese

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from getopt import getopt, GetoptError
from OkAPI import OkAPI
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
