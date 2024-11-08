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
import shutil
import yaml

from permanens.logger import get_logger
from permanens.consult import Consult

LOG = get_logger(__name__)

def action_consult (form=None, formfile=None):

    if form == None:

        if formfile == None:
            return False, 'formfile not loaded'

        with open(formfile, 'r') as f:
            form = yaml.safe_load(f)

    if form == None:
        return False, 'formfile not loaded'

    c = Consult()

    success, result = c.run (form)

    return success, result

def action_rerun (id):

    c = Consult()

    success, form = c.load_form(id)
    if not success:
        return form

    success, result = c.run (form)

    return success, result


def action_kill(cname=None):
    '''
    removes the consult with the ID given as argument
    '''
    if cname == None:
        return False, 'Empty risk assessment name'
    
    # TODO

    return True, 'OK'

def action_list(out='text'):
    '''
    lists all consults in the repository  
    '''
    c = Consult()
    consult_list = c.list(out)

    if out == 'text':
        for item in consult_list:
            print (item)
        return True, f'{len(consult_list)} items'

    return True, consult_list



