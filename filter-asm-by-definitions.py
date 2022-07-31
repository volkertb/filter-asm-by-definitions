#!/usr/bin/env python3
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: Copyright 2022 Volkert de Buisonjé
# SPDX-License-Identifier: Apache-2.0

import sys
from enum import Enum

ENCODING_ARG_PREFIX = "--encoding="
ASM_DEF_FILTER_PREFIX = "-D"
ASM_PRESERVED_DEF_PREFIX = "-P"
OUTPUT_FILE = "out.asm"
CONDITIONAL_DEFINITION_DIRECTIVES = ["IFDEF", "IFNDEF", "ELSEIFDEF", "ELSEIFNDEF"]


class MasmKeywordAction(Enum):
    TREAT_AS_CONTENT = 0
    INCLUDE_CODE_BLOCK = 1
    EXCLUDE_CODE_BLOCK = 2


def filter_file(input_file_path, encoding, allowlisted_asm_def_filters, definitions_to_reserve):
    print(f"Specified allowlisted IF(N)DEF filters: {allowlisted_asm_def_filters}")
    print(f"Specified IF(N)DEFs to preserve (keep variable): {definitions_to_reserve}")
    try:
        with open(input_file_path, 'r', encoding=encoding) as fstream:
            with open(OUTPUT_FILE, 'w', encoding=encoding) as fostream:

                line_iterator = iter(enumerate(fstream))

                try:
                    while True:
                        i, line = next(line_iterator)
                        directive, definition, label = get_directive_with_arg_and_label_from_line(line)

                        if directive == "IFDEF":
                            if definition in asm_defs_to_preserve:
                                fostream.write(line)
                                process_other_conditional_block(line_iterator, fostream,
                                                                allowlisted_asm_def_filters, definitions_to_reserve)
                            else:
                                if label is not None:
                                    fostream.write(label)
                                if definition in allowlisted_asm_def_filters:
                                    process_conditional_definition_true_block(line_iterator, fostream,
                                                                              allowlisted_asm_def_filters,
                                                                              definitions_to_reserve)
                                else:
                                    process_conditional_definition_false_block(line_iterator, fostream,
                                                                               allowlisted_asm_def_filters,
                                                                               definitions_to_reserve)
                        elif directive == "IFNDEF":
                            if definition in asm_defs_to_preserve:
                                fostream.write(line)
                                process_other_conditional_block(line_iterator, fostream,
                                                                allowlisted_asm_def_filters, definitions_to_reserve)
                            else:
                                if label is not None:
                                    fostream.write(label)
                                if definition in allowlisted_asm_def_filters:
                                    process_conditional_definition_false_block(line_iterator, fostream,
                                                                               allowlisted_asm_def_filters,
                                                                               definitions_to_reserve)
                                else:
                                    process_conditional_definition_true_block(line_iterator, fostream,
                                                                              allowlisted_asm_def_filters,
                                                                              definitions_to_reserve)
                        else:
                            allowlisted_asm_def_filters = add_to_allowlist_if_equ(line, allowlisted_asm_def_filters,
                                                                                  f"{input_file_path}:{i + 1}: ")
                            fostream.write(line)
                            # line = line.rstrip('\n')
                            # print(line)

                # Python's iterator has no hasNext equivalent. :/
                except StopIteration:
                    print("All lines in input file processed.")

    except UnicodeDecodeError:
        sys.exit(f"The specified input file {input_file_path} does not seem to have {encoding} encoding.\n"
                 f"Try specifying the correct encoding as an argument, using the `{ENCODING_ARG_PREFIX} prefix.\n"
                 f"(for instance `{ENCODING_ARG_PREFIX}IBM437`, which is typical for DOS sources)")


def process_conditional_definition_true_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                              definitions_to_reserve):
    ignore_remaining_lines_until_corresponding_endif = False
    nested_ignored_if_blocks = 0
    while True:
        i, line = next(line_iterator)
        directive, definition, label = get_directive_with_arg_and_label_from_line(line)

        allowlisted_asm_def_filters = add_to_allowlist_if_equ(line, allowlisted_asm_def_filters,
                                                              f"Input line {i + 1}: ")

        if directive == "ENDIF":
            if nested_ignored_if_blocks > 0:
                nested_ignored_if_blocks -= 1
            else:
                return

        if ignore_remaining_lines_until_corresponding_endif:
            if directive is not None and directive.startswith("IF"):
                nested_ignored_if_blocks += 1
            continue

        if directive == "IFDEF":
            if definition in asm_defs_to_preserve:
                fostream.write(line)
                process_other_conditional_block(line_iterator, fostream,
                                                allowlisted_asm_def_filters, definitions_to_reserve)
            else:
                if label is not None:
                    fostream.write(label)
                if definition in allowlisted_asm_def_filters:
                    process_conditional_definition_true_block(line_iterator, fostream,
                                                              allowlisted_asm_def_filters, definitions_to_reserve)
                else:
                    process_conditional_definition_false_block(line_iterator, fostream,
                                                               allowlisted_asm_def_filters, definitions_to_reserve)
        elif directive == "IFNDEF":
            if definition in asm_defs_to_preserve:
                fostream.write(line)
                process_other_conditional_block(line_iterator, fostream,
                                                allowlisted_asm_def_filters, definitions_to_reserve)
            else:
                if label is not None:
                    fostream.write(label)
                if definition in allowlisted_asm_def_filters:
                    process_conditional_definition_false_block(line_iterator, fostream,
                                                               allowlisted_asm_def_filters, definitions_to_reserve)
                else:
                    process_conditional_definition_true_block(line_iterator, fostream,
                                                              allowlisted_asm_def_filters, definitions_to_reserve)
        elif directive is not None and directive.startswith("IF"):
            # This is another IFx directive, not related to conditional definitions, so include the IFx in the output.
            fostream.write(line)
            process_other_conditional_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                            definitions_to_reserve)
        elif directive is not None and directive.startswith("ELSE"):
            ignore_remaining_lines_until_corresponding_endif = True
        else:
            allowlisted_asm_def_filters = add_to_allowlist_if_equ(line, allowlisted_asm_def_filters,
                                                                  f"Input line {i + 1}: ")
            fostream.write(line)


def process_conditional_definition_false_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                               definitions_to_reserve):
    nested_ignored_if_blocks = 0
    while True:
        i, line = next(line_iterator)
        directive, definition, _ = get_directive_with_arg_and_label_from_line(line)

        if directive == "ENDIF":
            if nested_ignored_if_blocks > 0:
                nested_ignored_if_blocks -= 1
            else:
                return

        if directive is not None and not directive.startswith("ELSE"):
            if directive.startswith("IF"):
                nested_ignored_if_blocks += 1
            continue

        if directive == "ELSE":
            # NOTE: Not strictly checking whether other IFxDEF between this ELSE and ENDIF will be encountered.
            process_conditional_definition_true_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                      definitions_to_reserve)
            return

        if directive == "ELSEIFDEF" and definition in allowlisted_asm_def_filters:
            # NOTE: Not strictly checking whether other IFxDEF between this ELSEIFDEF and ENDIF will be encountered.
            process_conditional_definition_true_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                      definitions_to_reserve)
            return

        if directive == "ELSEIFNDEF" and definition not in allowlisted_asm_def_filters:
            # NOTE: Not strictly checking whether other IFxDEF between this ELSEIFNDEF and ENDIF will be encountered.
            process_conditional_definition_true_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                      definitions_to_reserve)
            return

        if definition in asm_defs_to_preserve:
            if directive in ("ELSEIFDEF", "ELSEIFNDEF"):
                sys.exit(f"Line {i + 1} in input file: ELSEIFDEF or ELSEIFNDEF with definition \"definition\" that was"
                         "specified with -P (\"preserve\") option inside an IF(N)DEF that was excluded with a -D "
                         "(\"filter\") option. This is not currently supported by the script, and would have to be "
                         "debugged further.")


def process_other_conditional_block(line_iterator, fostream, allowlisted_asm_def_filters, definitions_to_reserve):
    while True:
        i, line = next(line_iterator)
        directive, definition, label = get_directive_with_arg_and_label_from_line(line)

        if directive == "IFDEF":
            if label is not None and definition not in asm_defs_to_preserve:
                fostream.write(label)
            if definition in allowlisted_asm_def_filters:
                process_conditional_definition_true_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                          definitions_to_reserve)
            elif definition in asm_defs_to_preserve:
                fostream.write(line)
                process_other_conditional_block(line_iterator, fostream,
                                                allowlisted_asm_def_filters, definitions_to_reserve)
            else:
                process_conditional_definition_false_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                           definitions_to_reserve)
        if directive == "IFNDEF":
            if label is not None and definition not in asm_defs_to_preserve:
                fostream.write(label)
            if definition in allowlisted_asm_def_filters:
                process_conditional_definition_false_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                           definitions_to_reserve)
            elif definition in asm_defs_to_preserve:
                fostream.write(line)
                process_other_conditional_block(line_iterator, fostream,
                                                allowlisted_asm_def_filters, definitions_to_reserve)
            else:
                process_conditional_definition_true_block(line_iterator, fostream, allowlisted_asm_def_filters,
                                                          definitions_to_reserve)

        allowlisted_asm_def_filters = add_to_allowlist_if_equ(line, allowlisted_asm_def_filters,
                                                              f"Input line {i + 1}: ")
        fostream.write(line)

        if directive == "ENDIF":
            return


def add_to_allowlist_if_equ(line, allowlist, log_prefix):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"

    if len(statement_components) < 3 or statement_components[1].upper() != "EQU":
        return allowlist

    equ_definition = statement_components[0]
    print(
        f"{log_prefix}: Encountered EQU directive for definition {equ_definition}, adding it to allowlist")
    allowlist.append(equ_definition)
    return allowlist


def get_directive_with_arg_and_label_from_line(line):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"
    if len(statement_components) < 1:
        return None, None, None

    label = None

    # Check if the line has a label
    if statement_components[0].endswith(':'):
        label = statement_components[0]
        print(f"Encountered label: {label}")
        statement_components = statement_components[1:]  # Remove the first item from the array
        if len(statement_components) < 1:
            return None, None, label

    directive = statement_components[0].upper()
    if directive in ("IFDEF", "IFNDEF", "ELSEIFDEF", "ELSEIFNDEF"):
        return directive, statement_components[1].upper(), label

    return directive, None, label


def is_start_of_excluded_definition(line, allowlisted_defs):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"
    first_statement_in_line_in_upper_case = statement_components[0].upper()
    if first_statement_in_line_in_upper_case in ("IFDEF", "ELSEIFDEF"):
        if statement_components[1] in allowlisted_defs:
            return True
    return False


def is_start_of_allowlisted_definition(line, allowlisted_defs):
    statement_components = line.lstrip().split()  # "default separator is any whitespace"
    first_statement_in_line_in_upper_case = statement_components[0].upper()
    if first_statement_in_line_in_upper_case in ("IFDEF", "ELSEIFDEF"):
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
    asm_defs_to_preserve = []

    if len(sys.argv[1:]) > 1:
        for argument in sys.argv[1:]:
            if argument.startswith(ENCODING_ARG_PREFIX):
                input_file_encoding = argument.removeprefix(ENCODING_ARG_PREFIX)
            elif argument.startswith(ASM_DEF_FILTER_PREFIX):
                asm_def_filters.append(argument.removeprefix(ASM_DEF_FILTER_PREFIX))
            elif argument.startswith(ASM_PRESERVED_DEF_PREFIX):
                asm_defs_to_preserve.append(argument.removeprefix(ASM_PRESERVED_DEF_PREFIX))

    if not set(asm_def_filters).isdisjoint(asm_defs_to_preserve):
        sys.exit("You cannot specify the same definition for both filtering (-D) and preserving (-P).")

    filter_file(sys.argv[1], input_file_encoding, asm_def_filters, asm_defs_to_preserve)
