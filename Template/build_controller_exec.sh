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

git clone --no-checkout https://ubwins.cse.buffalo.edu/git/swetankk/cse4589_pa3.git
cd cse4589_pa3 && git config core.sparseCheckout true && echo 'Controller/' >> .git/info/sparse-checkout && git checkout master && cd ..

# Build the executable
pyinstaller --onefile cse4589_pa3/Controller/controller.py

# Copy the binary and example topology file
cp dist/controller controller/
cp cse4589_pa3/Controller/example.topology controller/

# Cleanup
rm -rf build
rm -rf dist
rm -rf cse4589_pa3
rm controller.spec
