#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Volkert de Buisonjé

import sys

ENCODING_ARG_PREFIX = "--encoding="
ASM_DEF_FILTER_PREFIX = "-D"


def filter_file(input_file_path, encoding, allowlisted_asm_def_filters):
    print(f"Specified allowlisted IFDEF filters: {allowlisted_asm_def_filters}")
    try:
        with open(input_file_path, 'r', encoding=encoding) as fstream:
            currently_in_excluded_segment = False
            for line in fstream:

                allowlisted_asm_def_filters = add_to_allowlist_if_equ(line, allowlisted_asm_def_filters)

                directive, definition = get_directive_with_arg_from_line(line)

                if currently_in_excluded_segment:

                    if directive == "ELSEIFDEF":
                        if definition in allowlisted_asm_def_filters:
                            currently_in_excluded_segment = False
                        continue

                    if directive == "ENDIF":
                        currently_in_excluded_segment = False
                        continue

                else:
                    # Currently in an included (allowlisted) segment

                    if directive == "IFDEF":
                        if definition not in allowlisted_asm_def_filters:
                            currently_in_excluded_segment = True
                        continue

                    if directive == "IFNDEF":
                        if definition in allowlisted_asm_def_filters:
                            currently_in_excluded_segment = True
                        continue

                    if directive == "ELSEIFDEF":
                        currently_in_excluded_segment = True
                        continue

                    if directive == "ENDIF":
                        continue

                    line = line.rstrip('\n')
                    print(line)

    except UnicodeDecodeError:
        sys.exit(f"The specified input file {input_file_path} does not seem to have {encoding} encoding.\n"
                 f"Try specifying the correct encoding as an argument, using the `{ENCODING_ARG_PREFIX} prefix.\n"
                 f"(for instance `{ENCODING_ARG_PREFIX}IBM437`, which is typical for DOS sources)")


def add_to_allowlist_if_equ(line, allowlist):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"

    if len(statement_components) < 3 or statement_components[1].upper() != "EQU":
        return allowlist

    allowlist.append(statement_components[0])
    return allowlist


def get_directive_with_arg_from_line(line):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"
    if len(statement_components) < 1:
        return None, None
    directive = statement_components[0].upper()
    if directive == "IFDEF" or directive == "ELSEIFDEF":
        return directive, statement_components[1].upper()
    else:
        return directive, None


def is_start_of_excluded_definition(line, allowlisted_defs):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"
    first_statement_in_line_in_upper_case = statement_components[0].upper()
    if first_statement_in_line_in_upper_case == "IFDEF" or first_statement_in_line_in_upper_case == "ELSEIFDEF":
        if statement_components[1] in allowlisted_defs:
            return True
    return False


def is_start_of_allowlisted_definition(line, allowlisted_defs):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"
    first_statement_in_line_in_upper_case = statement_components[0].upper()
    if first_statement_in_line_in_upper_case == "IFDEF" or first_statement_in_line_in_upper_case == "ELSEIFDEF":
        if statement_components[1] in allowlisted_defs:
            return True
    return False


if __name__ == "__main__":
    input_file_encoding = "utf-8"
    if len(sys.argv[1:]) < 1:
        # See https://docs.python.org/3/library/sys.html#sys.exit
        sys.exit('You need to specify the path to the input file as the (first) command-line argument.\n'
                 f'Optionally, you can add the input file encoding (for instance `{ENCODING_ARG_PREFIX}IBM437`) '
                 f'as an additional argument. {input_file_encoding} will be assumed by default.')

    asm_def_filters = []

    if len(sys.argv[1:]) > 1:
        for argument in sys.argv[1:]:
            if argument.startswith(ENCODING_ARG_PREFIX):
                input_file_encoding = argument.removeprefix(ENCODING_ARG_PREFIX)
            elif argument.startswith(ASM_DEF_FILTER_PREFIX):
                asm_def_filters.append(argument.removeprefix(ASM_DEF_FILTER_PREFIX))

    filter_file(sys.argv[1], input_file_encoding, asm_def_filters)
