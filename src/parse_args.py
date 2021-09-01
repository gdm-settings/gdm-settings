#!/bin/python
import argparse
from get_theme_list import ThemeList

parser = argparse.ArgumentParser(description='set GDM theme and background'
                                , epilog="run '%(prog)s subcommand --help' for help about a specific subcommand"
                                , usage='%(prog)s [-h] subcommand {options}'
                                )

subparsers = parser.add_subparsers(title='subcommands', metavar=None, prog=parser.prog)

desc='set theme and/or background'
parser_set = subparsers.add_parser(name='set', aliases=['s'], help=desc, description=desc)
parser_set_arggroup = parser_set.add_mutually_exclusive_group(required=True)

parser_set_arggroup.add_argument('-r', '--re-apply', action='store_true', help='re-apply the same theme and background')
parser_set_arggroup.add_argument('-b', '--background', dest='opt_background', metavar='BACKGROUND', help='change background only')
parser_set_arggroup.add_argument("theme", nargs='?', help='name of GDM theme', metavar='theme', choices=ThemeList)
parser_set.add_argument('background', nargs='?', help='background image/color')

desc='list installed themes'
parser_list = subparsers.add_parser(name='list', aliases=['l'], help=desc, description=desc)
desc='list names of acceptable colors'
parser_list_colors = subparsers.add_parser(name='list-colors', aliases=['lc'], help=desc, description=desc)
desc='show manual page'
parser_manual = subparsers.add_parser(name='manual', aliases=['m'], help=desc, description=desc)
desc='describe some example commands'
parser_examples = subparsers.add_parser(name='examples', aliases=['e'], help=desc, description=desc)

desc='manage backup of default theme'
parser_backup = subparsers.add_parser(name='backup', aliases=['b'], help=desc, description=desc)
subparsers_backup = parser_backup.add_subparsers()
desc='update backup of default theme'
parser_backup_update = subparsers_backup.add_parser(name='update', aliases=['u'], help=desc, description=desc)
desc='restore default theme from backup'
parser_backup_restore = subparsers_backup.add_parser(name='restore', aliases=['r'], help=desc, description=desc)

desc='extract default theme'
parser_extract = subparsers.add_parser(name='extract', aliases=['x'], help=desc, description=desc)
parser_extract.add_argument('dir', nargs='?', help='extract to this directory')
parser_extract.add_argument('theme', nargs='?', metavar='theme', help='theme to extract (possible values: default,distro-default)', choices=['default', 'distro-default'])

args = parser.parse_args()