#!/usr/bin/env python3
# thoth-github-action
# Copyright(C) 2022 - Red Hat, Inc.
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


_RECOMMENDATION_TYPE = os.getenv("RECOMMENDATION_TYPE", "security")

advise_result = advise_here(recommendation_type=_RECOMMENDATION_TYPE)[0]

if advise_result.get("error") == True:
    if advise_result.get("error_msg") == "No direct dependencies found":
        raise Exception("No direct dependencies found for this repository.")

justifications = advise_result.get("report").get("products")[0].get("justification")

if any(justification.get("type") == "WARNING" for justification in justifications):
    vulnerabilities_report = ""

    for justification in justifications:
        if justification.get("type") == "WARNING":
            for k, v in justification.items():
                vulnerabilities_report += f"{k}: {v}"
                vulnerabilities_report += "\n"
            vulnerabilities_report += "\n\n"

    print(vulnerabilities_report)
    raise Exception("Vulnerabilities have been detected in your dependencies.")
