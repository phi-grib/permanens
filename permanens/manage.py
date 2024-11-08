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
from permanens.utils import consult_repository_path, id_generator

LOG = get_logger(__name__)

def action_consult (formfile):

    form = None
    with open(formfile, 'r') as f:
        form = yaml.safe_load(f)

    if form == None:
        return False, 'formfile not loaded'
    
    c = Consult()

    success, result = c.run (form)

    return success, result


def action_kill(cname):
    '''
    removes the last step from the ra tree or the whole tree if no step is specified
    '''
    if not cname:
        return False, 'Empty risk assessment name'

    return True, 'OK'

def action_list(out='text'):
    '''
    if no argument is provided lists all ranames present at the repository 
    otherwyse lists all versions for the raname provided as argument
    '''
    rdir = consult_repository_path()
    if os.path.isdir(rdir) is False:
        return False, 'The risk assessment name repository path does not exist. Please run "permanens -c config".'

    output = []
    num_ranames = 0
    if out != 'json':
        LOG.info('Consults found in repository:')
        
    for x in os.listdir(rdir):
        xpath = os.path.join(rdir,x) 

        # discard if the item is not a directory
        if not os.path.isdir(xpath):
            continue

        num_ranames += 1
        if out != 'json':
            LOG.info('\t'+x)

        output.append(x)

    LOG.debug(f'Retrieved list of risk assessments from {rdir}')
    
    # web-service
    if out=='json':
        return True, output

    return True, f'{num_ranames} risk assessment(s) found'

def action_info(cname, out='text'):
    '''
    provides a list with all steps for ranames present at the repository 
    '''
    # instantiate a ra object
    ra = Consult(cname)

    succes, results = ra.load()
    if not succes:
        return False, results


    LOG.debug(f'Retrieved general info for {cname}')

    # for ikey in info:
    #     ielement = info[ikey]
    #     for jkey in ielement:
    #         jelement = ielement[jkey]
    #         if out != 'json':
    #             LOG.info(f'{ikey} : {jkey} : {jelement}')

    # # web-service
    # if out=='json':
    #     return True, info

    return True, f'completed info for {cname}'

