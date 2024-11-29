#! -*- coding: utf-8 -*-

# Description    permanens command
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2022 Manuel Pastor
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
import yaml

from permanens.logger import get_logger
from permanens.consult import Consult

LOG = get_logger(__name__)
c = Consult()

def action_consult (form=None, formfile=None, id=None):
    ''' uses the input data provided in the arguments to run the consult  
    '''
     
    # input is a file (typically from command line)
    if formfile != None:
        if not os.path.isfile(formfile):
            return False, 'input file not found'

        with open(formfile, 'r') as f:
            form = yaml.safe_load(f)

    # input is a form (passed as argument or loaded from input file)
    if form == None:
        return False, 'failed to load input data'
        
    # c = Consult()

    success, result = c.run (form, id)

    return success, result

def action_rerun (id):
    ''' tries to load a form with the ID given as argument, saved in the repository 
        and run the consult 
    '''

    # c = Consult()

    success, form = c.load_form(id)
    if not success:
        return form

    success, result = c.run (form, id)

    return success, result

def action_retrieve (id):
    ''' tries to load a form with the ID given as argument, saved in the repository 
    '''

    # c = Consult()

    success, form = c.load_form(id)
    return success, form


def action_kill(cname=None):
    '''
    removes the consult with the ID given as argument
    '''
    if cname == None:
        return False, 'no consult ID provided'
    
    # c = Consult()

    succes, result = c.kill(cname)

    return succes, result

def action_list(out='text'):
    '''
    lists all consults in the repository  
    '''

    # c = Consult()

    consult_list = c.list(out)

    if out == 'text':
        for item in consult_list:
            print (item)
        return True, f'{len(consult_list)} items'

    return True, consult_list



