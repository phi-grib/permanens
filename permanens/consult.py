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
        cname = id_generator()

        # assign path
        self.cpath = consult_path(cname)
        

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

        # rename other yaml file in the historic describing the same step as bk_
        step = self.ra['step']
        
        files_to_rename = []

        rahistpath = os.path.join (self.cpath,'hist')

        for ra_hist_file in os.listdir(rahistpath):
            if not ra_hist_file.startswith('ra_'):
                continue
            ra_hist_item = os.path.join(rahistpath, ra_hist_file)
            if os.path.isfile(ra_hist_item):
                idict = {}
                with open(ra_hist_item, 'r') as pfile:
                    idict = yaml.safe_load(pfile)
                    if 'ra' in idict:
                        if 'step' in idict['ra']:
                            if step == idict['ra']['step']:
                                files_to_rename.append(ra_hist_file)

            for ifile in files_to_rename:
                ipath = os.path.join(rahistpath,ifile)
                if os.path.isfile(ipath):
                    bk_name = os.path.join(rahistpath, 'bk_'+ ifile[3:])
                    i=1
                    while os.path.isfile(bk_name):
                        bk_name = os.path.join(rahistpath, f'bk_{ifile[3:-5]}_{str(i)}.yaml')
                        i=i+1
                    os.rename(ipath, bk_name)

        # save in the historic file
        time_label = time.strftime("_%d%b%Y_%H%M%S", time.localtime()) 
        rahist = os.path.join (rahistpath,f'ra{time_label}.yaml')
        shutil.copyfile(rafile, rahist)

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
