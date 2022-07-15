#!/usr/bin/env python3
# thoth-github-action
# Copyright(C) 2022 Maya Costantini
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

"""Entrypoint for the Thoth Adviser GitHub Action."""

import configparser
import os
import subprocess
import sys

from thamos.exceptions import ConfigurationError
from thamos.exceptions import NoRequirementsFile

from typing import List
from typing import Optional
from typing import Tuple


_REQUIREMENTS_FORMAT = os.getenv("INPUT_REQUIREMENTS_FORMAT", "pipenv")
_GENERATE_SUMMARY = os.getenv("INPUT_GENERATE_SUMMARY", True)
_IGNORE_CVE = os.getenv("INPUT_IGNORE_CVE")
_CONSIDER_DEV_DEPENDENCIES = os.getenv("INPUT_CONSIDER_DEV_DEPENDENCIES", False)
_RUNTIME_ENVIRONMENT = os.getenv("INPUT_RUNTIME_ENVIRONMENT")
_GITHUB_SUMMARY_FILE = os.environ["GITHUB_STEP_SUMMARY"]

_REQUIREMENT_FORMAT_TO_FILE = {"pip": "requirements.txt", "pipenv": "Pipfile", "setup.cfg": "setup.cfg"}
_RUNTIME_ENVIRONMENTS = frozenset(["ubi-8-py-3.8", "rhel-8-py-3.8", "fedora-35-py-3.10", "fedora-34-py-3.9"])

_CONFIG_CONTENT = """\
host: khemenu.thoth-station.ninja
tls_verify: true
requirements_format: {requirements_format}

runtime_environments:
  - name: {runtime_environment}
    operating_system:
      name: {os_name}
      version: '{os_version}'
    python_version: '{python_version}'
    recommendation_type: security

"""


def _parse_environment(runtime_environment: Optional[str]) -> List:
    """Parse environment name for configuration."""
    if runtime_environment not in _RUNTIME_ENVIRONMENTS:
        raise Exception("Invalid environment name")

    return runtime_environment.split("-")


def _prepare_requirements_file(requirements_format: str) -> None:
    """Get requirements file name from requirements format."""
    requirements_file = _REQUIREMENT_FORMAT_TO_FILE.get(requirements_format)
    if not requirements_file:
        raise ValueError(
            f"Requirements format {requirements_format} is not valid. "
            f"Valid requirement formats are {', '.join([*_REQUIREMENT_FORMAT_TO_FILE])}"
        )

    if not os.path.isfile(requirements_file):
        raise NoRequirementsFile(
            f"No dependency requirements file found for requirements format {requirements_format}"
            " at the root of the repository. "
            f"Valid requirements file names are {', '.join([*_REQUIREMENT_FORMAT_TO_FILE.values()])}"
        )

    if requirements_file == "setup.cfg":
        cfgparser = configparser.ConfigParser()
        cfgparser.read(requirements_file)

        with open("requirements.txt", "w") as requirements_txt_file:
            requirements_txt_file.writelines("\n".join(cfgparser["options"]["install_requires"].splitlines()))


def _prepare_config_file(requirements_format: str, runtime_environment: Optional[str]) -> str:
    """Prepare the Thamos configuration file."""
    if requirements_format not in _REQUIREMENT_FORMAT_TO_FILE:
        raise ValueError(
            f"Requirements format {requirements_format} is not valid. "
            f"Valid requirement formats are {', '.join([*_REQUIREMENT_FORMAT_TO_FILE])}"
        )

    if requirements_format == "setup.cfg":
        requirements_format = "pip"

    if runtime_environment:
        os_name, os_version, _, python_version = _parse_environment(runtime_environment)
        config_file_content = _CONFIG_CONTENT.format(
            requirements_format=requirements_format,
            runtime_environment=os_name + os_version,
            os_name=os_name,
            os_version=os_version,
            python_version=python_version,
        )

        with open(".thoth.yaml", "w") as config_file:
            config_file.write(config_file_content)

    summary_content = ""

    try:
        subprocess.run(["thamos", "check"])
        if _GENERATE_SUMMARY:
            summary_content += ":heavy_check_mark: Thoth configuration check passed \n"
    except subprocess.CalledProcessError as e:
        print(e.output)
        if _GENERATE_SUMMARY:
            summary_content += ":x: Thoth configuration check failed \n"
        raise ConfigurationError from e

    return summary_content


def _get_thamos_args() -> Tuple[List, str]:
    """Get optional thamos command line arguments."""
    thamos_args = []
    summary_content = ""

    if _IGNORE_CVE:
        if _GENERATE_SUMMARY:
            summary_content += f"Ignoring CVE: {_IGNORE_CVE} \n"
        thamos_args.extend(["--labels", f"allow-cve={_IGNORE_CVE}"])

    if _CONSIDER_DEV_DEPENDENCIES:
        if _GENERATE_SUMMARY:
            summary_content += ":wrench: Considering development dependencies for the resolution \n"
        thamos_args.extend(["--dev"])

    return thamos_args, summary_content


def _get_search_ui_link() -> str:
    """Get link to results in Thoth Search UI."""
    summary_content = ""
    with open(".thoth_last_analysis_id", "r") as last_analysis_id_file:
        analysis_id = last_analysis_id_file.read()

    search_ui_link = f"https://thoth-station.ninja/search/advise/{analysis_id}/summary"
    summary_content += f":bulb: Browse dependency analysis results in Thoth Search UI: {search_ui_link}"

    return summary_content


summary_content = ""

summary_content += _prepare_config_file(_REQUIREMENTS_FORMAT, _RUNTIME_ENVIRONMENT)
_prepare_requirements_file(_REQUIREMENTS_FORMAT)

thamos_args, thamos_args_summary_content = _get_thamos_args()
summary_content += thamos_args_summary_content

status = subprocess.run(["thamos", "advise"] + thamos_args, stdout=subprocess.PIPE)

if status.returncode != 0:
    summary_content += ":x: Dependency resolution failed \n"
    exit_code = 1
else:
    summary_content += ":heavy_check_mark: No vulnerabilities were detected in your dependencies \n"
    exit_code = 0

summary_content += _get_search_ui_link()

if _GENERATE_SUMMARY:
    with open(_GITHUB_SUMMARY_FILE, "w") as summary_file:
        summary_file.write(summary_content)

sys.exit(exit_code)
