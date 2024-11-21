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

import yaml
import os
import pickle
import json
import numpy as np
from permanens.utils import consult_repository_path, model_repository_path, id_generator
from permanens.logger import get_logger

LOG = get_logger(__name__)

class Consult:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''
        # assign path
        self.cpath = consult_repository_path()

        # assign estimator
        self.model = os.path.join(model_repository_path(),'rf.pkl')

        # load estimators + rules as a list of pipelines
        # TODO
        
    def run (self, form, cname=None):
        ''' function called when receiving an input form 
        '''
        if cname == None:
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

    def condition (self, form, names):
        nvarx = len(names)
        
        xtest = np.zeros((1,nvarx))
        for ikey in form:
            ival = form[ikey]

            # for lists
            if isinstance(form[ikey], list):
                for item in ival:
                    if item in names:
                        xtest[0,names.index(item)] = 1
                        print ('assigned from list: ', item)

            # for sex and age
            if ikey in names:
                xtest[0,names.index(ikey)] = ival
                print('assigned from key: ', ikey, ival)

        return True, xtest

    def predict (self, form, cname):
        ''' uses the form to run the prediction pipeline
        '''
        LOG.info (f'predicting {cname} form')
        result = {'cname' : cname} 

        # open estimator
        with open(self.model, 'rb') as handle:
            model = pickle.load(handle)
            names = pickle.load(handle)

        # conditions form to adapt to the estimator requirements
        success, xtest = self.condition (form, names)
        if not success:
            return False, 'unable to condition input form'

        # submit to rule-based pipeline
        #TODO

        # submit to model
        r = model.predict(xtest)
        r_proba = model.predict_proba(xtest)
        result['outcome'] = r.tolist()[0]
        result['probability'] = r_proba.tolist()[0]

        return True, result

    def list (self, format):
        ''' lists all the forms stored in the repository
        '''
        return os.listdir(self.cpath)
    
    def kill (self, cname):
        ''' deletes the consult with the ID provided as argumen from the repository
        '''
        formfile = os.path.join (self.cpath, cname)
        if os.path.isfile(formfile):
            os.remove(formfile)
            return True, 'OK'
        else:
            return False, 'file not found'
