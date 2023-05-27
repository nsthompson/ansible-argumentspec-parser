#!/usr/bin/env python3
#
# Utility to parse Ansible role meta/argument_specs.yml
# file and generate an SVG for documentation purposes
#
# Copyright (C) 2023 Nick Thompson
# All Rights Reserved
#
import os

import rich_click as click
from rich.console import Console
import oyaml as yaml


def generate_tree(argument_spec, indent_level=0):
    tree = ""

    for key, value in argument_spec.items():
        if "description" in value:
            description = value["description"]
        else:
            description = ""

        if "type" in value:
            key_type = value["type"]
        else:
            key_type = ""

        if "required" in value:
            required = value["required"]
        else:
            required = ""

        if "choices" in value:
            indentation = "    " * indent_level
            choices = f"\n{indentation}    - ".join(str(choice) for choice in value["choices"])
        else:
            choices = None

        indentation = "    " * indent_level

        # Add tree symbols and indentation
        if choices is not None:
            tree_string = (
                f'{indentation}|- [bold blue]{key}[/]: {description} '
                f'[italic](Type: {key_type}, Required: {required})[/]\n{indentation}    '
                f'[bold red]Available Choices[/]\n{indentation}    - {choices}\n'
            )
        else:
            tree_string = (
                f'{indentation}|- [bold blue]{key}[/]: {description} '
                f'[italic](Type: {key_type}, Required: {required})[/]\n'
            )

        tree += tree_string

        if "options" in value:
            tree += generate_tree(value["options"], indent_level + 1)

    return tree


# Collect filename at runtime
@click.command()
@click.option(
    '--file',
    'file_path',
    required=True,
    type=click.Path(exists=True, readable=True),
    help='Path to Ansible role argument_specs.yml'
)
@click.option(
    '--output-dir',
    'output_dir',
    required=True,
    type=click.Path(exists=True, writable=True),
    help='Path for generated SVG files'
)
def parse_file(file_path, output_dir):
    with open(file_path, 'r', encoding='utf-8') as file:
        argspec_dict = yaml.load(file, Loader=yaml.FullLoader)
        tree = generate_tree(argspec_dict["argument_specs"]["main"]["options"])

    console = Console(record=True)
    console.print(tree)

    # Capture Path for SVG Filename
    filename = os.path.dirname(os.path.dirname(file_path)).split('/')[-1]
    console.save_svg(f"{output_dir}/{filename}.svg", title="Argument Spec")


if __name__ == "__main__":
    parse_file()  # pylint: disable=no-value-for-parameter
