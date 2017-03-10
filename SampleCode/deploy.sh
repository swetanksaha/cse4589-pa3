#!/bin/bash
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

if [ "$#" -ne 3 ]; then
    echo "Usage: deploy HOSTNAME USER UPLOAD-PATH"
    exit
fi

hostname=$1
user=$2
upath=$3

folder_name="swetankk"

# Package
cd ${folder_name}/ && tar -zcvf ../${folder_name}_pa3.tar * && cd .. --exclude-vcs

# Upload
scp ${folder_name}_pa3.tar $user@$hostname:$upath/

# Cleanup
rm ${folder_name}_pa3.tar
