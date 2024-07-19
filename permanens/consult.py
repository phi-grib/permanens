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

import pickle
import shutil
import yaml
import os
import time
import hashlib
from permanens.utils import ra_path
from permanens.logger import get_logger
LOG = get_logger(__name__)

class Consult:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self, raname):
        ''' constructor '''

        # internal data
        self.raname = raname
        self.rapath = ra_path(raname)
        self.workflow = None  
        
        # default, these are loaded from a YAML file
        self.ra = {
            'ID': None,
            'workflow_name': None,
            'step': 0,
            'active_nodes_id': [],
            'tasks_completed': None,
            'notes': None
        }
        self.general = {
            'endpoint': {},
            'title': None,
            'problem_formulation': None,
            'uncertainty': None, 
            'administration_route': None,
            'species': None,
            'regulatory_frameworks': None,
            'workflow_custom': None,
            'substances': []
        }
        self.results = []
        self.notes = []
        # self.assessment = None
        self.placehoders = {
            'general_description': 'Descriptive text about this study',
            'background': 'Any relevant information',
            'endpoint': 'Toxicological endpoint(s) of interest',
            'title': 'Descriptive name for this study',
            'problem_formulation': 'Short description of the toxicological issue to be adressed',
            'uncertainty': 'Comments about the acceptable uncertainty levels', 
            'administration_route': 'Administration routes of the toxican to be considered',
            'species': 'Biological species to be considered',
            'regulatory_framework': 'Regulatory bodies for which this study can be of interest',
            'workflow_custom': 'File describing the workflow. If empty the ASPA workflow will be used instead',
            'substances': {
                'name': ' Substance name or names separated by a colon',
                'id': ' Substance ID or IDs separated by a colon',
                'casrn': ' Substance CAS-RN or CAS-RNs separated by a colon',
            }
        }

    def load(self, step=None):       
        ''' load the Consult object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        if not os.path.isdir (self.rapath):
            return False, f'Risk assessment "{self.rapath}" not found'

        # load the main class dictionary (p) from this yaml file
        ra_file_name = os.path.join (self.rapath,'ra.yaml')
        if not os.path.isfile(ra_file_name):
            return False, f'Risk assessment definition {ra_file_name} file not found'

        # load status from yaml
        yaml_dict = {}
        try:
            with open(ra_file_name, 'r') as pfile:
                yaml_dict = yaml.safe_load(pfile)
        except Exception as e:
            return False, f'error:{e}'
        
        # if a defined step is requested
        if step is not None:
            try:
                step = int(step)
            except:
                return False, 'step must be a positive int'

            found = False
            # check first if the requested step is the last one
            if not self.checkStep(yaml_dict, step):
                ra_hist_path = os.path.join (self.rapath,'hist')
                for ra_hist_file in os.listdir(ra_hist_path):
                    ra_hist_item = os.path.join(ra_hist_path, ra_hist_file)
                    if os.path.isfile(ra_hist_item):
                        idict = {}
                        with open(ra_hist_item, 'r') as pfile:
                            idict = yaml.safe_load(pfile)
                        if self.checkStep(idict, step):
                            yaml_dict = idict
                            found = True
                            break
                                
                if not found:
                    return False, 'step not found'                

        # validate yaml_dict
        keylist = ['ra', 'general', 'results', 'notes']
        for ikey in keylist:
            if yaml_dict[ikey]!=None:
                self.__dict__[ikey]=yaml_dict[ikey]

        # load workflow
        if self.ra['step']>0 : 
            self.workflow = Workflow(self.raname, self.ra['workflow_name'])

        return True, 'OK'

    def save (self):
        ''' saves the Consult object to a YAML file
        '''
        rafile = os.path.join (self.rapath,'ra.yaml')
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

        rahistpath = os.path.join (self.rapath,'hist')

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
