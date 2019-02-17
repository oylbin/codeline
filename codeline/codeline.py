import os
import sys
import re
import operator
import logging
import tempfile
import fnmatch
import click
import sh
from terminaltables import AsciiTable


# python table lib
# https://pypi.org/project/PrettyTable/  last update: 2013
# https://pypi.org/project/tableprint/  last update: 2018
# https://pypi.org/project/terminaltables/ last update: 2016
# https://pypi.python.org/pypi/tabulate last update: 2019

def should_ignore(filename, ignore_dirs):
    for pat in ignore_dirs:
        if fnmatch.fnmatch(filename, pat):
            return True
    return False


def filelist(file_extensions, ignore_dirs):
    args = ['ls-files', '--']
    for ext in file_extensions:
        args.append("*." + ext)
    for filename in sh.git(*args):
        if not should_ignore(filename.strip(), ignore_dirs):
            yield filename.strip()


def blamefile(filename, pattern, author_line_dict):
    logger = logging.getLogger("codeline")
    logger.info(filename)
    cmd = sh.Command('git')
    cmd = cmd.bake("blame", "--no-color", "--line-porcelain", filename)
    logger.debug("COMMAND: {}".format(cmd))

    def process_output(line):
        if type(line) is bytes:
            line = line.decode('utf-8', errors="ignore")

        match_result = pattern.search(line)
        if match_result is None:
            return
        author = match_result.group(1)
        if author in author_line_dict:
            author_line_dict[author] += 1
        else:
            author_line_dict[author] = 1

    cmd(_out=process_output, _tty_out=False)

    logger.debug(author_line_dict)


def print_summary(author_line_dict):
    total_line_count = sum(author_line_dict.values())
    sorted_x = sorted(author_line_dict.items(), key=operator.itemgetter(1), reverse=True)
    # for name, count in sorted_x:
    #     print("{:>24}: {:>10}, {:10.2f}%".format(name, count, 100.0 * count / total_line_count))

    table_data = [["name", "line count", "radio"]]
    for name, count in sorted_x:
        table_data.append([name, count, "{:.2f}%".format(100.0 * count / total_line_count)])

    table = AsciiTable(table_data)
    table.justify_columns[1] = 'right'
    table.justify_columns[2] = 'right'

    print(table.table)
    # print(tabulate(table_data[1:], table_data[0], tablefmt="pipe"))


@click.command()
@click.option("--file-ext", required=True, multiple=True, help="File extension to be counted")
@click.option("--ignore-dir", default=None, multiple=True, help="dir to be ignored, Unix shell-style wildcards")
def main(**options):
    logging.basicConfig(format='%(asctime)-15s %(message)s')
    logger = logging.getLogger("codeline")
    logger.setLevel(logging.INFO)

    # TODO ls-file 中文名称的问题
    project_name = os.path.basename(os.getcwd())
    print("project: {}".format(project_name))

    pattern = re.compile("^author (.*)")

    author_line_dict = {}

    for filename in filelist(options['file_ext'], options['ignore_dir']):
        blamefile(filename, pattern, author_line_dict)

    print_summary(author_line_dict)
