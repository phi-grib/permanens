#! -*- coding: utf-8 -*-

# Description    Context wrapps calls to predict and build to
# support models making use of extenal input sources
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
# permanens is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with permanens. If not, see <http://www.gnu.org/licenses/>.

import functools
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def supress_log(logger: logging.Logger):
    """Decorator for suprerss logs during objects workflow

    Logs we are entering a supress log routine and
    disables the logger setting the minimum message level at
    interpreter level.
    """
    def decorator(func):
        @functools.wraps(func)
        def supressor(*args, **kwargs):
            logger.warning('Entering OBJECTS workflow. Logger will be disabled'
                           ' below error level')
            logging.disable(logging.WARNING)
            func_results = func(*args, **kwargs)
            logging.disable(logging.NOTSET)
            logger.debug('Logger enabled again!')
            return func_results
        return supressor
    return decorator


def get_log_file() -> Path:
    """ Returns the log file path

    The path of the log file is given by
    appdirs.user_log_dir
    """
    log_filename_path = './'
    log_filename_path = Path(log_filename_path)
    
    # creeate dir if it does not exist
    if not log_filename_path.exists():
        log_filename_path.mkdir(parents=True)

    log_filename = log_filename_path / 'permanens.log'  # append file name

    # check if exists to not erase current file
    if not log_filename.exists():
        log_filename.touch()

    return log_filename


def get_logger(name) -> logging.Logger:
    """ inits a logger and adds the handlers.

    If the logger is already created doesn't adds new handlers
    since those are set at interpreter level and already exists.
    """    
    # create logger
    logger = logging.getLogger(name)

    # set base logger level to DEBUG but fine tu the handlers
    # for custom level
    logger.setLevel(logging.DEBUG)

    # create formatter fdor file handler (more explicit)
    file_formatter = logging.Formatter(
        '%(levelname)-8s [%(asctime)s] %(thread)d - %(name)s - %(message)s'
    )

    # formater for stream handler (less info)
    stdout_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    log_file = get_log_file()  # Create the log file
    # create console and file handler
    # if not already created
    if not logger.handlers:

        # Send DEBUG to a rotating log file
        # Limit the size to 1000000Bytes ~ 1MB 
        fh = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)
        fh.set_name('filehandler')
        fh.setLevel('DEBUG')
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

        # send INFO to the console (stdin)
        ch = logging.StreamHandler(sys.stdout)
        ch.set_name('streamhandler')
        ch.setLevel('INFO')
        ch.setFormatter(stdout_formatter)
        logger.addHandler(ch)

        return logger
        
    # if there already handlers just return the logger
    # since its already configured
    else:
        return logger
