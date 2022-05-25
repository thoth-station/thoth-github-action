#!/usr/bin/env python3
# thoth-github-action
# Copyright(C) 2022 - Maya Costantini
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Convert setup.cfg to requirements.txt."""

import configparser
import os
import sys


def _convert_setup_to_requirements(setup_file_path: str) -> None:
    """Convert setup.cfg to requirements.txt."""
    cfgparser = configparser.ConfigParser()
    cfgparser.read(setup_file_path)
    requirements_file_path = os.path.join(os.path.dirname(os.path.abspath(setup_file_path)), "requirements.txt")

    with open(requirements_file_path, "w") as requirements_file:
        requirements_file.write(cfgparser["options"]["install_requires"])


if __name__ == "__main__":
    _convert_setup_to_requirements(sys.argv[1])
