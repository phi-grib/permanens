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

from permanens.utils import consult_repository_path, model_repository_path, id_generator, hashfile
from permanens.logger import get_logger
from permanens.mapping import condition_to_label, label_to_condition, atc_to_label, label_to_atc

LOG = get_logger(__name__)

age_ranges = ['18-24','25-34','35-44','45-54','55-64','65-74','75-84','85-94'] 
sex_code = ['female','male']
VAR_MAX = 50

class Consult:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''
        # assign path
        self.cpath = consult_repository_path()
        
        # obtain a list with all estimators and all model information
        model_repo = model_repository_path()
        self.model_names = []
        self.model_dicts = []
        self.model_labels = []
        # self.rules_dict = {}
        for iname in os.listdir (model_repo):
            
            # only for files in dill format
            if not iname.endswith('.dill'):
                continue

            ipath = os.path.join(model_repo,iname)
            self.model_names.append(ipath)
            
            hfile = hashfile(ipath)
        
            try:
                with open(ipath, 'rb') as handle:
                    idict = dill.load(handle)
            except:
                LOG.error ('unable to load model info')
                continue
            
            idict['model_hash'] = hfile
            self.model_dicts.append(idict)
        
            # models are identified by the descrition and a hashed unique ID
            if 'description' in idict:
                dfile = idict['description']
            else:
                dfile = 'unknown'
            # models are identified by the descrition and a hashed unique ID
            if 'endpoint' in idict:
                efile = idict['endpoint']
            else:
                efile = 'unknown'
            
            self.model_labels.append((efile, hfile, dfile))
        
        self.modelID = 0

        # use first model as default
        # self.set_model(0)
        
        # # reading a pre-build yaml file containing a ruleset
        # self.rules_dict['rules'] = {}
        # self.rules_dict['rules_pred'] = []

        # rpath = os.path.join(model_repo,'rules_en.yaml')
        # if os.path.isfile(rpath):
        #     with open(rpath,'r',encoding='utf8') as f:
        #         self.rules_dict['rules']['en'] = yaml.safe_load(f)

        #     # get a list of relevant predictors (used by any rule) 
        #     for item in self.rules_dict['rules']['en']:
        #         for iitem in item['rules']:
        #             ipredictor = iitem['predictor']
        #             if ipredictor not in self.rules_dict['rules_pred']:
        #                 self.rules_dict['rules_pred'].append(ipredictor)

        # # other lenguajes
        # rpath = os.path.join(model_repo,'rules_es.yaml')
        # if os.path.isfile(rpath):
        #     with open(rpath,'r',encoding='utf8') as f:
        #         self.rules_dict['rules']['es'] = yaml.safe_load(f)
        #         rpath = os.path.join(model_repo,'rules_es.yaml')
        
        # rpath = os.path.join(model_repo,'rules_ca.yaml')
        # if os.path.isfile(rpath):
        #     with open(rpath,'r',encoding='utf8') as f:
        #         self.rules_dict['rules']['ca'] = yaml.safe_load(f)
                 
        # # mapp
        # self.mapp = {}
        # rpath = os.path.join(model_repo,'predictor_mappings.yaml')
        # if os.path.isfile(rpath):
        #     with open(rpath,'r',encoding='utf8') as f:
        #         self.mapp = yaml.safe_load(f)     

        # #TODO: read the static adice formatted for the GUI
        # self.advice = {}
        
        # apath = os.path.join(model_repo,'advice_en.yaml')
        # if os.path.isfile(apath):
        #     with open(apath,'r', encoding='utf8') as f:
        #         self.advice['en'] = yaml.safe_load(f)
        # apath = os.path.join(model_repo,'advice_es.yaml')
        # if os.path.isfile(apath):
        #     with open(apath,'r', encoding='utf8') as f:
        #         self.advice['es'] = yaml.safe_load(f)

        LOG.info ('INITIALIZATION COMPLETE')
        
    def set_model (self, modelID, lang=None):
        ''' defines the model with the given modelID as the current model
            if the lang parameter is provided, the predictor variable names are
            translated
        '''

        self.modelID = modelID

        LOG.info(f'setting model to {modelID}')
        if modelID >= len (self.model_dicts):
            return False, 'modeID out of range'
        
        self.model_name = self.model_names[modelID]
        self.model_dict = self.model_dicts[modelID]

        # extract top-10 predictor for drugs and conditions
        var_importance = self.model_dict['var_importance']

        # initialize predictors
        self.predictors={'drugs': [], 'conditions':[]}

        # assign predictors
        predictors_dict = self.model_dict['predictors_dict']
        for item in ['drugs', 'conditions']:
            for ivar in var_importance:
                if ivar in predictors_dict[item]:
                    self.predictors[item].append(ivar)
        
        result = {}
        result['model_description'] = self.model_dict['description']
        result['model_metrics_training'] = self.model_dict['metrics_fitting']
        result['model_metrics_test'] = self.model_dict['metrics_prediction']
        result['model_hash'] = self.model_dict['model_hash']

        result['conditions_labels'] = condition_to_label (self.predictors['conditions'])
        result['drugs_labels'] = atc_to_label (self.predictors['drugs'])

        # # for back-compatibility only
        # result['conditions'] = self.predictors['conditions'] 
        # result['drugs'] = self.predictors['drugs'] 

        return True, result

    def get_model_labels (self):
        ''' returns model labels'''
        return self.model_labels
       
    def run (self, form, cname=None, lang='en'):
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
        success, result = self.predict(form, cname, lang)
        if not success:
            return False, result
           
        # # send to rules
        # success, result_rules = self.apply_rules(form, lang)
        # if not success:
        #     return True, result

        # merge results of prediction and rules
        # result['treatment']= result_rules
         
        return success, result

    def save_form (self, form, cname):
        ''' saves the Consult object to a YAML file
        '''
        consultfile = os.path.join (self.cpath, cname)

        form['model_hash'] = self.model_dict['model_hash']

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
        
        if 'model_hash' in form:
            input_hash = form['model_hash']
            found = False
            for i,imodel in enumerate(self.model_labels):
                if imodel[1] == input_hash:
                    self.set_model(i)
                    found = True
            if not found:
                return False, 'No model matching'
        
        return True, form

    def condition_model (self, form, names):
        ''' compares the form values with the names to setup an appropriate
            input string for the model
        '''
        nvarx = len(names)
        xtest_np = np.zeros((1,nvarx))

        if 'events' not in form:
            form['events'] == 0
            
        if form['events'] == 0:
            form ['last_event'] = 100

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
                if ikey == 'age':
                    ival = int (np.round(ival/10.0))
                xtest_np[0,names.index(ikey)] = ival
                # print('assigned from key: ', ikey, ival)

        # convert to pandas dataframe 
        xtest_pd = pd.DataFrame(xtest_np)
        xtest_pd.columns = names

        return True, xtest_pd, xtest_np
    
    # def condition_rules (self, form, rules_pred):
    #     ''' process the form to generate a dictionary suitable for testing the rules
    #     '''        
    #     x_rules = {}  # dictionary key:value containing only predictors used by the rule

    #     for ikey in form:
    #         ival = form[ikey]

    #         # for lists
    #         if isinstance(form[ikey], list):
    #             for item in ival:
    #                 if item in rules_pred:
    #                     if not item in x_rules:
    #                        x_rules [item] = True

    #         # for sex and age
    #         if ikey in rules_pred:
    #             if not ikey in x_rules:
    #                 x_rules[ikey] = ival
        
    #     return True, x_rules

    def predict (self, form, cname, lang = None):
        ''' uses the form to run the prediction pipeline
        '''

        if 'modelID' in form and form['modelID'] != self.modelID:
            
            self.modelID = form['modelID']
            
            LOG.info (f'setting model {self.modelID} for local instance')

            self.model_name = self.model_names[self.modelID]
            self.model_dict = self.model_dicts[self.modelID]

            # extract top-10 predictor for drugs and conditions
            var_importance = self.model_dict['var_importance']

            # initialize predictors
            self.predictors={'drugs': [], 'conditions':[]}

            # assign predictors
            predictors_dict = self.model_dict['predictors_dict']
            for item in ['drugs', 'conditions']:
                for ivar in var_importance:
                    if ivar in predictors_dict[item]:
                        self.predictors[item].append(ivar)

        LOG.info (f'predicting {cname} form, for model {self.modelID}')

        # results dictionary will contain a lot of information with the result of the analysis
        result = {'cname' : cname} 

        model = self.model_dict['model']
        calib = self.model_dict['calib']
        explainer = self.model_dict['explainer']
        names = model.feature_names_in_.tolist()

        conditions = []
        if 'conditions_labels' in form:
            conditions = label_to_condition (form['conditions_labels'])

        drugs = []
        if 'drugs_labels' in form:
            drugs = label_to_atc (form['drugs_labels'])

        # conditions form to adapt to the estimator requirements
        success, xtest_pd, xtest_np = self.condition_model (form, names)
        if not success:
            return False, 'unable to condition input form'

        # submit to model
        r = model.predict(xtest_pd).tolist()[0]
        irisk = calib.predict_proba(xtest_pd).tolist()[0][1]

        # list of predictors
        predictors = ['sex', 'age', 'events', 'last_event']
        predictors += conditions
        predictors += drugs

        # in case of negatives, pass an empty list
        importance_sel = [] 
        
        # only if the prediction is positive
        # if r==1:  
        #TODO: results vary slighly in every run. Check this potential solution
        # https://github.com/marcotcr/lime/issues/119
        
        # for j in range (10):
        #     exp = explainer.explain_instance(xtest_np[0], model.predict_proba, num_features=30, num_samples= 5000, labels=(1), top_labels=1)
            
        #     # exp = explainer.explain_instance(xtest_np[0], model.predict_proba, labels=(1), num_features=40, top_labels=1)
        #     importance_all = exp.as_list(label=1)
        #     print (importance_all)

        xint = xtest_np[0].astype(np.int32)
        np.random.seed(1)
        exp = explainer.explain_instance(xint, model.predict_proba, num_features=len(names), num_samples=10000)
        # exp = explainer.explain_instance(xint, calib.predict_proba, num_features=len(names), num_samples=10000)
        importance_all = exp.as_list(label=1)     

        for i in importance_all:
            ilabel = i[0]

            # LIME includes predictors in labels which either start with the predictor name (e.g.,'anxiolytic=0')
            # or are inserted between unqualities (e.g., '4.00 < age <= 6.00')
            for ipredictor in predictors:
                if ilabel.startswith(ipredictor) or " "+ipredictor+" " in ilabel:
                    importance_sel.append( (ipredictor, i[1]) )
                    break
                    
        result['outcome'] = r
        result['probability'] = irisk
        result['input'] = form

        ####################################################
        # OBSOLETE
        # result['decil_info'] = self.model_dict['decil_info']
        ####################################################

        # Extract the histogram for this particular segment of population
        # Obtain all the histogram information
        risk_histogram = self.model_dict['risk_histogram']
        risk_histogram_bins = self.model_dict['risk_histogram_bins']
        
        # Identify the sex/age segment
        histogram_sex_index = form['sex']
        histogram_age_index = int(np.floor((form['age']+5)/10.0))-2
        if histogram_age_index < 0:
            histogram_age_index = 0
        elif histogram_age_index > 7:
            histogram_age_index = 7

        # Histogram for this particular sex/age segment
        irisk_histogram=risk_histogram[histogram_sex_index][histogram_age_index][0]
        irisk_histogram_bins=risk_histogram_bins[histogram_sex_index][histogram_age_index][0]

        # proportion of observed positives for the 9 age segments considered
        risk_segment = self.model_dict['risk_segment'][histogram_sex_index]

        # endpoint name
        iendpoint = self.model_dict['endpoint']
        
        # risk of peers
        iriskpeers = risk_segment[histogram_age_index]

        # proportion of population with risk lower or equal than the patient risk
        # note that we use the high resolution histograma (100 bins) to obtain a better estimation
        population_below = 0.0
        for ibar in range(len (irisk_histogram)):
            if irisk > irisk_histogram_bins[ibar+1]: # uper limit of risk
                population_below+=irisk_histogram[ibar] 
            else:
                # proportion of the last bar
                pnorm = (irisk - irisk_histogram_bins[ibar]) / (irisk_histogram_bins[ibar+1] - irisk_histogram_bins[ibar])
                population_below+= pnorm * irisk_histogram[ibar] 
                break

        # The histogram information is high-resolution (usually 100 bins), but we only need bins for graphic representation
        step = int(len(irisk_histogram)/20)
        graphic_histogram = [float(np.sum(irisk_histogram[i:i+step])) for i in range(0,len(irisk_histogram), step)]
        graphic_histogram_bins = [float(irisk_histogram_bins[i]) for i in range(0,len(irisk_histogram_bins), step)]

        # information needed for generating graphics
        result['probability_peers'] = iriskpeers
        result['histogram'] = graphic_histogram 
        result['histogram_bins'] = graphic_histogram_bins

        result['population_below'] = population_below
        result['risk_max'] = float(irisk_histogram_bins[-1])

        ####################################################
        # OBSOLETE, REMOVE!!!!!!
        # result['perc_above'] = 0.0
        # result['histogram_bar'] = 0
        ####################################################

        # narrative
        result['narrative'] = { 
            'risk_individual' : f"Based on the information you entered, the risk of this <s>{form['age']}<e>-year-old <s>{sex_code[histogram_sex_index]}<e> individual is {irisk*100.0:.2f}%." ,
            'risk_peers': f"Among <s>{sex_code[histogram_sex_index]}<e> aged <s>{age_ranges[histogram_age_index]}<e> years presenting to the ED, the risk of <s>{iendpoint}<e> months is <s>{iriskpeers*100.0:.2f}<e>%",
            'distribution': f"The risk in this individual is <s>{irisk/iriskpeers:.2f}<e> times the risk of age-matched <s>{sex_code[histogram_sex_index]}<e> peers and places its risk above <s>{population_below*100:.1f}<e>% of age-matched <s>{sex_code[histogram_sex_index]}<e> peers."
        }

        ####################################################
        # OBSOLETE
        # result['model_description'] = self.model_dict['description'] 
        # result['model_metrics_training'] = self.model_dict['metrics_fitting']
        # result['model_metrics_test'] = self.model_dict['metrics_prediction']
        ####################################################

        result['explanation']= importance_sel

        ####################################################
        # OBSOLETE
        model_percentils = self.model_dict['percentils']
        ####################################################

        # pred_percentil = 100
        # for i, pi in enumerate(model_percentils):
        #     if pi > irisk :
        #         pred_percentil = i
        #         break
        # result['percentil'] = pred_percentil
        
        # pred_decil = 10
        # for i, d in enumerate(result['decil_info']):
        #     if d['pmax'] > irisk:
        #         pred_decil = i+1
        #         break
        # result['decil'] = pred_decil

        return True, result

    # def apply_rules (self, form, lang='en'):
    #     ''' returns a piece of text depending if the forms have certain contents, defined by some rules
    #     '''
    #     if not lang in self.rules_dict['rules']:
    #         return False, f'no rules found for lenguaje {lang}'

    #     if len(self.rules_dict['rules'][lang]) == 0:
    #         return False, 'no rules found'
        
    #     results = []

    #     # submit to rule-based pipeline
    #     success, x_rules = self.condition_rules (form, self.rules_dict['rules_pred'])
    #     if not success:
    #         return False, 'unable to process form'

    #     # print (x_rules)

    #     # process rules
    #     for irule in self.rules_dict['rules'][lang]:
    #         conn = irule['connect']
    #         ruleset = irule['rules']
    #         nrule_true = 0
    #         for iirule in ruleset:
    #             # rules are formed by a dictionary with 4 keys
    #             # predictor: name of the predictor variable
    #             # presence: [True|False], true if the value is True and the predictor is present in the form (for binary predictors)
    #             #                         true if the value is False and predictor is absent in the form (for binary predictors)
    #             # min: true if the predictor is > rule value (for sex, age or #visits)
    #             # max: true if the predictor is < rule value (for sex, age or #visits)
    #             predictor_name = iirule['predictor']

    #             if predictor_name in x_rules:
    #                 if 'presence' in iirule:
    #                     if iirule['presence'] == True:
    #                         nrule_true +=1

    #                 elif 'min' in iirule:
    #                     if x_rules[predictor_name] > iirule['min']:
    #                         nrule_true +=1

    #                 elif 'max' in iirule:
    #                     if x_rules[iirule[0]] < iirule['max']:
    #                         nrule_true +=1
    #             else:
    #                 if 'presence' in iirule and iirule['presence'] == False:
    #                     nrule_true +=1


    #         if conn == 'or':
    #             if nrule_true > 0:
    #                 results.append (irule['result'])
    #         else:
    #             if nrule_true == len (ruleset):
    #                 results.append (irule['result'])

    #     return True, results

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

    def save_care (self, care):
        ''' save care information in YAML file
        '''

        if 'id' in care:
            careid = care['id']
        else:
            return False, 'id not found'

        carefile = os.path.join (self.cpath, careid+'_care')

        with open(carefile,'w') as f:
            f.write(yaml.dump(care))

        return True, 'OK'
    
    def load_care (self, id):
        ''' load care information from YAML file
        '''

        carefile = os.path.join (self.cpath, id+'_care')
        if not os.path.isfile(carefile):
            return False, 'file not found'

        with open(carefile,'r') as f:
            care = yaml.safe_load(f)

        return True, care