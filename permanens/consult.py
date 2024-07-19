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

import shutil
import yaml
import os
import time
from permanens.utils import consult_path, id_generator
from permanens.logger import get_logger
LOG = get_logger(__name__)

class Consult:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''

        # generate unique ID
        self.cname = id_generator()

        # assign path
        self.cpath = consult_path(self.cname)
        
    def run (self, form):

        print (self.cname, form)

        return True, 'OK'

    def load(self):       
        ''' load the Consult object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        if not os.path.isdir (self.cpath):
            return False, f'Consult "{self.cpath}" not found'

        # load the main class dictionary (p) from this yaml file
        consult_file_name = os.path.join (self.cpath,'consult.yaml')
        if not os.path.isfile(consult_file_name):
            return False, f'Consult definition {consult_file_name} file not found'

        # load status from yaml
        yaml_dict = {}
        try:
            with open(consult_file_name, 'r') as pfile:
                yaml_dict = yaml.safe_load(pfile)
        except Exception as e:
            return False, f'error:{e}'
        
        return True, 'OK'

    def save (self):
        ''' saves the Consult object to a YAML file
        '''
        rafile = os.path.join (self.cpath,'ra.yaml')
        dict_temp = {
            'ra': self.ra,
            'general': self.general, 
            'results': self.results,
            'notes': self.notes
        }
        with open(rafile,'w') as f:
            f.write(yaml.dump(dict_temp))


    def getStatus(self):
        ''' return a dictionary with RA status
        '''

        # Update the number of tasks completed and the number of notes
        self.ra['tasks_completed'] = len (self.results)
        self.ra['notes'] = len (self.notes)

        return {'ra':self.ra}


    def getVal(self, key):
        ''' returns self.dict value for a given key
        '''
        if key in self.ra:
            return self.ra[key]
        else:
            return None

    def setVal(self, key, value):
        ''' sets self.dict value for a given key, either replacing existing 
            values or creating the key, if it doesn't exist previously
        '''
        # for existing keys, replace the contents of 'value'
        if key in self.ra:
            self.ra[key] = value
        # for new keys, create a new element with 'value' key
        else:
            self.ra[key] = value
