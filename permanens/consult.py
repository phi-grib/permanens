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
from permanens.utils import consult_repository_path, id_generator
from permanens.logger import get_logger

LOG = get_logger(__name__)

class Consult:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''
        # assign path
        self.cpath = consult_repository_path()

        # load estimator
        
    def run (self, form):
        ''' function called when receiving an input form 
        '''
        # generate unique ID
        cname = id_generator()

        # save form
        success = self.save_form(form, cname)
        if not success:
            return False, 'unable to save input'
        
        # send to prediction 
        success, result = self.predict(form, cname)

        return success, result

    def save_form (self, form, cname):
        ''' saves the Consult object to a YAML file
        '''
        consultfile = os.path.join (self.cpath, cname)

        with open(consultfile,'w') as f:
            f.write(yaml.dump(form))

        return True
    
    def load_form (self, cname):
        ''' load form from YAML file
        '''
        consultfile = os.path.join (self.cpath, cname)

        if not os.path.isfile(consultfile):
            return False, 'not found'

        form = None
        with open(consultfile,'r') as f:
            form = yaml.safe_load(f)

        if form == None:
            return False, 'unable to load form'
        
        return True, form

    def predict (self, form, cname):

        # conditions form to adapt to the estimator requirements

        LOG.info (f'predicting {cname} form')

        result = 'OK'

        return True, result

    def list (self, format):
        return os.listdir(self.cpath)