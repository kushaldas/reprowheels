#!/usr/bin/env python
import click
import os
import sys
from pip_requirements_parser import RequirementsFile

@click.command()
@click.argument('requirements_file')
def parse_requirements(requirements_file):
    "Parse requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"Requirements file not found {requirements_file=}")
        sys.exit(1)
    rf = RequirementsFile.from_file(requirements_file)   
    data = rf.to_dict()
    # Now loop through the requirements
    for req in data["requirements"]:
        if len(req["specifier"]) > 0:
            project_name = req['name']
            spec = req['specifier'][0]
            print(f"{project_name=} {spec=}")


if __name__ == "__main__":
    parse_requirements()

