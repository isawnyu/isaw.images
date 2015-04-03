#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
script to run after running migrate.sh
"""

import argparse
from functools import wraps
from isaw.images import package, proof_sheet, validate_path
import logging
import os
import re
import sys
import traceback

DEFAULTLOGLEVEL = logging.WARNING

def arglogger(func):
    """
    decorator to log argument calls to functions
    """
    @wraps(func)
    def inner(*args, **kwargs): 
        logger = logging.getLogger(func.__name__)
        logger.debug("called with arguments: %s, %s" % (args, kwargs))
        return func(*args, **kwargs) 
    return inner    


@arglogger
def main (args):
    """
    main functions
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)

    real_path = validate_path(args.tgt, type='directory')
    logger.info("beginning post-migration on {0}".format(real_path))
    # get a list of all the directories at path, determine which are image packages, open and validate
    directories = [o for o in os.listdir(real_path) if os.path.isdir(os.path.join(real_path,o))]
    logger.debug("found {0} sub-directories".format(len(directories)))
    for d in directories:
        pkg = package.Package()
        try:
            pkg.open(os.path.join(path,d))
        except IOError, e:
            logger.info("failed trying to open directory '{0}' as a package: {1}".format(d, e))
        else:
            if pkg.validate():
                logger.info("directory '{0}' is a valid image package".format(d))
                pass
            else:
                logger.warning("successfully opened directory '{0}' as a package, but it failed to validate".format(d))
        del pkg
    proof_sheet.Proof(real_path)
    logger.info("wrote proof sheet on {0}".format(os.path.join(real_path, 'index.html')))
    logger.info("finished post-migration on {0}".format(real_path))


if __name__ == "__main__":
    log_level = DEFAULTLOGLEVEL
    log_level_name = logging.getLevelName(log_level)
    logging.basicConfig(level=log_level)

    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument ("-l", "--loglevel", type=str, help="desired logging level (case-insensitive string: DEBUG, INFO, WARNING, ERROR" )
        parser.add_argument ("-v", "--verbose", action="store_true", default=False, help="verbose output (logging level == INFO")
        parser.add_argument ("-vv", "--veryverbose", action="store_true", default=False, help="very verbose output (logging level == DEBUG")
        parser.add_argument('tgt', help='target directory in which to run post-migration')
        args = parser.parse_args()
        if args.loglevel is not None:
            args_log_level = re.sub('\s+', '', args.loglevel.strip().upper())
            try:
                log_level = getattr(logging, args_log_level)
            except AttributeError:
                logging.error("command line option to set log_level failed because '%s' is not a valid level name; using %s" % (args_log_level, log_level_name))
        if args.veryverbose:
            log_level = logging.DEBUG
        elif args.verbose:
            log_level = logging.INFO
        log_level_name = logging.getLevelName(log_level)
        logging.getLogger().setLevel(log_level)
        if log_level != DEFAULTLOGLEVEL:
            logging.warning("logging level changed to %s via command line option" % log_level_name)
        else:
            logging.info("using default logging level: %s" % log_level_name)
        logging.debug("command line: '%s'" % ' '.join(sys.argv))
        main(args)
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print "ERROR, UNEXPECTED EXCEPTION"
        print str(e)
        traceback.print_exc()
        os._exit(1)
