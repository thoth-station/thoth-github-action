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

"""Analyze the output of adviser report for CVE."""


import json
import sys

from json.decoder import JSONDecodeError


def _process_advise_result() -> str:
    """Process advise results from generated output file."""
    with open(sys.argv[1], "r") as results_file:
        try:
            results = json.load(results_file)
            if results.get("error"):
                return "\N{Cross Mark} " + results.get("error_msg")
            return "No vulnerabilities detected in your dependencies."
        except JSONDecodeError as json_decode_error:
            raise json_decode_error


if __name__ == "__main__":
    print(_process_advise_result())
