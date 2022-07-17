#!/usr/bin/env python3
import sys

ENCODING_ARG_PREFIX = "--encoding="
ASM_DEF_FILTER_PREFIX = "-D"


def filter_file(input_file_path, encoding, allowlisted_asm_def_filters):
    print(f"Specified allowlisted IFDEF filters: {allowlisted_asm_def_filters}")
    try:
        with open(input_file_path, 'r', encoding=encoding) as fstream:
            for line in fstream:
                line = line.rstrip('\n')
                print(line)
    except UnicodeDecodeError:
        sys.exit(f"The specified input file {input_file_path} does not seem to have {encoding} encoding.\n"
                 f"Try specifying the correct encoding as an argument, using the `{ENCODING_ARG_PREFIX} prefix.\n"
                 f"(for instance `{ENCODING_ARG_PREFIX}IBM437`, which is typical for DOS sources)")


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
