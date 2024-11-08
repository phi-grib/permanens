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
from permanens import __version__
from permanens.config import configure
from permanens.manage import action_consult, action_kill, action_list, action_rerun


LOG = get_logger(__name__)

def main():

    LOG.debug('-------------NEW RUN-------------\n')

    results = None
    parser = argparse.ArgumentParser(description='permanens')

    parser.add_argument('-c', '--command',
                        action='store',
                        choices=['config', 'consult', 'kill', 'list' ],
                        help='Action type: \'config\' or \'kill\' or \'list\' ',
                        required=True)

    parser.add_argument('-i', '--id',
                        help='Consultation id',
                        required=False)

    parser.add_argument('-d', '--directory',
                        help='configuration dir',
                        required=False)
    
    parser.add_argument('-a', '--action',
                        help='action',
                        required=False)
    
    parser.add_argument('-f', '--formfile',
                        help='consultation input',
                        required=False)

    args = parser.parse_args()

    if args.formfile is not None:
        if not os.path.isfile(args.formfile):
            LOG.error(f'Input file {args.formfile} not found')
            return 

    if args.command == 'config':
        success, results = configure(args.directory, (args.action == 'silent'))
        if not success:
            LOG.error(f'{results}, configuration unchanged')

    elif args.command == 'consult':
        if args.id != None:
            success, results = action_rerun(args.formfile) 

        if args.formfile != None:
            success, results = action_consult(formfile=args.formfile)  

    elif args.command == 'list':
        success, results = action_list()   

    elif args.command == 'kill':
        success, results = action_kill(args.id)   
    
    if results is not None and type(results) != dict:
        LOG.info (results)

if __name__ == '__main__':
    main()