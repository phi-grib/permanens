#! -*- coding: utf-8 -*-

# Description    permanens command
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2024 Manuel Pastor
#
# This file is part of permanens
#
# permanens is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with permanens. If not, see <http://www.gnu.org/licenses/>.

import os
import argparse
from permanens.logger import get_logger
# from permanens import __version__
from permanens.config import configure
from permanens.manage import action_new, action_kill, action_list, action_info


LOG = get_logger(__name__)

def main():

    LOG.debug('-------------NEW RUN-------------\n')

    results = None
    parser = argparse.ArgumentParser(description='permanens')

    parser.add_argument('-c', '--command',
                        action='store',
                        choices=['config', 'new', 'kill', 'list', 'info' ],
                        help='Action type: \'config\' or \'new\' or \'kill\' or \'list\' or \'info\' ',
                        required=True)

    parser.add_argument('-r', '--raname',
                        help='Name of RA',
                        required=False)

    parser.add_argument('-s', '--step',
                        help='RA workflow step',
                        required=False)
    
    parser.add_argument('-v', '--version',
                        help='RA version',
                        required=False)  

    parser.add_argument('-d', '--directory',
                        help='configuration dir',
                        required=False)


    args = parser.parse_args()

    if args.infile is not None:
        if not os.path.isfile(args.infile):
            LOG.error(f'Input file {args.infile} not found')
            return 

    if args.command == 'config':
        success, results = configure(args.directory, (args.action == 'silent'))
        if not success:
            LOG.error(f'{results}, configuration unchanged')

    elif args.command == 'new':
        if (args.raname is None or args.outfile is None ):
            LOG.error('permanens new : raname and output file arguments are compulsory')
            return
        success, results = action_new(args.raname, args.outfile)

    elif args.command == 'list':
        success, results = action_list()   

    elif args.command == 'info':
        if (args.raname is None ):
            LOG.error('permanens info : raname argument is compulsory')
            return
        success, results = action_info(args.raname)   

    elif args.command == 'kill':
        if (args.raname is None):
            LOG.error('permanens kill : raname argument is compulsory')
            return
        success, results = action_kill(args.raname)   

    
    if results is not None and type(results) != dict:
        LOG.info (results)

if __name__ == '__main__':
    main()