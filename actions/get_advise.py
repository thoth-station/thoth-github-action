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

"""Get advise from Thoth on the current repository."""

import os

from thamos.lib import advise_here

_REQUIREMENTS_FORMAT = os.getenv("REQUIREMENTS_FORMAT", "pipenv")


os.system(f"sed -i 's/pip-tools/{_REQUIREMENTS_FORMAT}/g' actions/ubuntu_config_template.yaml")

with open("actions/ubuntu_config_template.yaml", "r") as file:
    print(file.read())

os.system("thamos config --no-interactive --template actions/ubuntu_config_template.yaml")

advise_result = advise_here(src_path="..", recommendation_type="security")[0]

if advise_result.get("error"):
    error_message = advise_result.get("error_msg")
    if advise_result.get("report").get("stack_info"):
        for stack_info in advise_result.get("report").get("stack_info"):
            for k, v in stack_info.items():
                print(f"{k}: {v}")
            print("\n")
    raise Exception(error_message)
