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
# import pickle
import dill
import pandas as pd
import numpy as np

from permanens.utils import consult_repository_path, model_repository_path, id_generator
from permanens.logger import get_logger

LOG = get_logger(__name__)
VAR_MAX = 10

class Consult:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''
        # assign path
        self.cpath = consult_repository_path()

        # assign estimator
        # self.model_name = os.path.join(model_repository_path(),'rf.pkl')
        self.model_name = os.path.join(model_repository_path(),'model-rf.dill')

        # open estimator
        with open(self.model_name, 'rb') as handle:
            self.model_dict = dill.load(handle)

        predictors_dict = self.model_dict['predictors_dict']

        self.predictors_ord={}
        self.predictors_ord['drugs'] = []
        self.predictors_ord['conditions'] = []
        
        # extract top-10 predictor for drugs and conditions
        var_importance = self.model_dict['var_importance']
        for item in ['drugs', 'conditions']:
            for ivar in var_importance:
                if ivar in predictors_dict[item]:
                    if len (self.predictors_ord[item]) < VAR_MAX:
                        self.predictors_ord[item].append(ivar)
                    else:
                        break

        LOG.info ('INITIALIZATION COMPLETE')
        

    def get_predictors (self):
        ''' provides a list of VAR_MAX predictors for drugs and conditions categories, which can
            be used as selectable predictor variables in the front-end
        '''
        if self.predictors_ord['drugs'] != [] and self.predictors_ord['conditions'] != []:
            return True, self.predictors_ord
        return False, 'predictors undefined'

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
        ''' compares the form values with the names to setup an appropriate
            input string for the model
        '''
        nvarx = len(names)
        
        xtest_np = np.zeros((1,nvarx))
        for ikey in form:
            ival = form[ikey]

            # for lists
            if isinstance(form[ikey], list):
                for item in ival:
                    if item in names:
                        xtest_np[0,names.index(item)] = 1
                        # print ('assigned from list: ', item)

            # for sex and age
            if ikey in names:
                xtest_np[0,names.index(ikey)] = ival
                # print('assigned from key: ', ikey, ival)

        # convert to pandas dataframe 
        xtest_pd = pd.DataFrame(xtest_np)
        xtest_pd.columns = names

        return True, xtest_pd, xtest_np

    def predict (self, form, cname):
        ''' uses the form to run the prediction pipeline
        '''
        LOG.info (f'predicting {cname} form')
        result = {'cname' : cname} 

        model = self.model_dict['model']
        explainer = self.model_dict['explainer']
        names = model.feature_names_in_.tolist()

        # conditions form to adapt to the estimator requirements
        success, xtest_pd, xtest_np = self.condition (form, names)
        if not success:
            return False, 'unable to condition input form'

        # submit to rule-based pipeline
        #TODO

        # submit to model
        r = model.predict(xtest_pd).tolist()[0]
        p = model.predict_proba(xtest_pd).tolist()[0]

        importance_sel = [] # in case of negatives, pass an empty list
        if r==1:
            exp = explainer.explain_instance(xtest_np[0], model.predict_proba, labels=(1), num_features=40, top_labels=1)
            importance_all = exp.as_list(label=1)
            for i in importance_all:
                ilabel = i[0]
                if ' > 0.0' in ilabel:
                    importance_sel.append( (ilabel[:-7], i[1]))
                
        result['outcome'] = r
        result['probability'] = p
        result['input'] = form
        result['decil_info'] = self.model_dict['decil_info']
        result['model_description'] = self.model_dict['description'] 
        result['model_metrics_training'] = self.model_dict['metrics_fitting']
        result['model_metrics_test'] = self.model_dict['metrics_prediction']
        result['explanation']= importance_sel
        model_percentils = self.model_dict['percentils']

        pred_percentil = 100
        for i, pi in enumerate(model_percentils):
            if pi > p[1] :
                pred_percentil = i
                break
        result['percentil'] = pred_percentil
        
        pred_decil = 10
        for i, d in enumerate(result['decil_info']):
            if d['pmax'] > p[1]:
                pred_decil = i+1
                break
        result['decil'] = pred_decil

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
