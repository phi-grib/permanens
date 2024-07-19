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

from permanens.logger import get_logger
from permanens.consult import Consult
from permanens.utils import ra_repository_path, ra_path, id_generator

LOG = get_logger(__name__)

def action_new(raname, outfile=None):
    '''
    Create a new risk assessment tree, using the given name.
    This creates the development version "dev",
    copying inside default child classes
    '''
    if not raname:
        return False, 'empty risk assessment name'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if raname == 'test':
        return False, 'the name "test" is disallowed, please use any other name'

    # raname directory with /dev (default) level
    ndir = ra_path(raname)
    if os.path.isdir(ndir):
        return False, f'Risk assessment {raname} already exists'
    try:
        os.mkdir(ndir)
        os.mkdir(os.path.join(ndir,'hist'))
        os.mkdir(os.path.join(ndir,'repo'))
        LOG.debug(f'{ndir}, {ndir}/hist and {ndir}/repo created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    # Copy templates
    wkd = os.path.dirname(os.path.abspath(__file__))
    template_names = ['ra.yaml', 'workflow.csv']

    for cname in template_names:
        src_path = os.path.join (wkd, 'default', cname)
        try:
            shutil.copy(src_path, ndir)
        except:
            return False, f'Unable to copy {cname} file'

    LOG.debug(f'copied risk assessment templates from {src_path} to {ndir}')

    # Instantiate Consult
    ra = Consult(raname)
    success, results = ra.load()
    if not success:
        return False, results

    # Include RA information 
    ra.setVal('ID', id_generator() )

    # Save
    ra.save()

    # Show template
    yaml = ra.getTemplate()
    
    if outfile is not None:
        with open(outfile,'w') as f:
            f.write(yaml)

    return True, f'New risk assessment {raname} created'

def action_kill(raname, step=None):
    '''
    removes the last step from the ra tree or the whole tree if no step is specified
    '''
    if not raname:
        return False, 'Empty risk assessment name'

    ndir = ra_path(raname)

    if not os.path.isdir(ndir):
        return False, f'Risk assessment {raname} not found'

    # Remove the whole tree
    if step is None:
        try:
            shutil.rmtree(ndir, ignore_errors=True)
        except:
            return False, f'Failed to remove risk assessment {raname}'

        return True, f'Risk assessment {raname} removed'

    # Remove last step
    if step == 1:
        return False, 'the first step cannot be removed'

    # New value of step
    new_step = step-1

    # load RA
    ra = Consult(raname)
    success, results = ra.load()
    if not success:
        return False, results

    last_step = ra.getVal('step')
    if step!=last_step:
        return False, 'only the last step can be removed'


    shutil.copy(ra_new, os.path.join(ndir,'ra.yaml'))
    
    # remove the ra to delete 
    success, ra_delete = getConsultHistoric(raname, step)
    if not success:
        return False, f'unable to remove file {ra_delete}'

    os.remove(ra_delete)

    return True, 'OK'

def action_list(out='text'):
    '''
    if no argument is provided lists all ranames present at the repository 
    otherwyse lists all versions for the raname provided as argument
    '''
    rdir = ra_repository_path()
    if os.path.isdir(rdir) is False:
        return False, 'The risk assessment name repository path does not exist. Please run "permanens -c config".'

    output = []
    num_ranames = 0
    if out != 'json':
        LOG.info('Risk assessment(s) found in repository:')
        
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

def action_info(raname, out='text'):
    '''
    provides a list with all steps for ranames present at the repository 
    '''
    # instantiate a ra object
    ra = Consult(raname)

    succes, results = ra.load()
    if not succes:
        return False, results

    # get a dictionary with the ra.yaml contents that can
    # be passed to the GUI or shown in screen
    info = ra.getGeneralInfo()

    LOG.debug(f'Retrieved general info for {raname}')

    for ikey in info:
        ielement = info[ikey]
        for jkey in ielement:
            jelement = ielement[jkey]
            if out != 'json':
                LOG.info(f'{ikey} : {jkey} : {jelement}')

    # web-service
    if out=='json':
        return True, info

    return True, f'completed info for {raname}'

def getPath(raname):
    '''
    returns the path to the RA folder for ra raname
    '''
    # instantiate a ra object
    ra = Consult(raname)

    succes, results = ra.load()
    if not succes:
        return False, results
    
    return True, ra.rapath

def getRepositoryPath(raname):
    '''
    returns the path to the repository folder for ra raname
    '''
    # instantiate a ra object
    ra = Consult(raname)

    succes, results = ra.load()
    if not succes:
        return False, results
    
    repo_path = os.path.join(ra.rapath, 'repo')
    return True, repo_path
