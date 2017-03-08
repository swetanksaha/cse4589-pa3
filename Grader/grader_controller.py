#!/usr/bin/python
#
# This file is part of CSE 489/589 Grader.
#
# CSE 489/589 Grader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# CSE 489/589 Grader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with CSE 489/589 Grader. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "Swetank Kumar Saha (swetankk@buffalo.edu)"
__copyright__ = "Copyright (C) 2017 Swetank Kumar Saha"
__license__ = "GNU GPL"
__version__ = "1.0"

import argparse
import os
import sys
import traceback
import time
import signal

import utils
import remote_api

parser = argparse.ArgumentParser(description='CSE 489/589 Grader Controller v'+__version__)

requiredArgs = parser.add_argument_group('required named arguments')
requiredArgs.add_argument('-c', '--config', dest='config', type=argparse.FileType('r'), nargs=1, help='configuration file', required=True)
requiredArgs.add_argument('-d', '--dir-assignment', dest='assignment', type=str, nargs=1, help='path to directory where assignment files will be stored/built [on remote machine relative to "base-dir" in grader.cfg]', required=True)
requiredArgs.add_argument('-s', '--submission', dest='submission', type=str, nargs=1 , help='path to submission tarball', required=True)
requiredArgs.add_argument('-ctrl', '--controller_path', dest='controller', type=str, nargs=1 , help='path to controller executable [on local machine]', required=True)
requiredArgs.add_argument('-t', '--test', dest='test', type=str, nargs=1, help='test name', required=True)

optionalArgs = parser.add_argument_group('optional named arguments')
optionalArgs.add_argument('-nu', '--no-upload', dest='no_upload', action='store_true', help='suppress file upload')
optionalArgs.add_argument('-nb', '--no-build', dest='no_build', action='store_true', help='suppress submission build')

if __name__ == '__main__':
    args = parser.parse_args()

    cfg = utils.readConfiguration(args.config[0])
    test_name = args.test[0]
    remote_api.ASSIGNMENT_PATH = os.path.join(cfg.get('Assignment', 'base-dir'), args.assignment[0])
    tarball = args.submission[0]

    for server in utils.GRADING_SERVERS_HOSTNAME:
        print
        print server
        # Upload submission
        if not args.no_upload:
            utils.print_regular('Uploading submission ...')
            remote_api.copy_file_to(cfg, server, tarball, os.path.basename(tarball), verbose=True)

        # Build submission
        if not args.no_build:
            utils.print_regular('Building submission ...')
            ret_code = remote_api.run_cmd(cfg, server, 'tar -xvf %s; make clean; make' % (os.path.basename(tarball)), async=False, verbose=True)
            if ret_code != 0:
                utils.print_error('FAILED')
                sys.exit(1)
            else: utils.print_success('OK')

    try:
        print
        utils.print_regular('Grading for: %s ...' % (test_name.upper()))
        import pa3_grader
        getattr(pa3_grader, test_name)(args.controller[0], cfg)
    except:
        traceback.print_exc()
        utils.print_error('EXIT: Grader encountered an error!')
    finally:
        remote_api.cleanup(cfg)
        utils.cleanup()
