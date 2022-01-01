#!/bin/python
import os, sys, argparse
import functions, variables

ThemeList=functions.get_theme_list()
functions.elevated_commands_list.elevator("sudo")

# Fuctions for ArgumentParser
def set_theme(args):
    if args.re_apply:
        print('re-apply')
    elif args.opt_background:
        functions.set_background(args.opt_background)
    else:
        if not os.path.exists(variables.TempDir):
            os.mkdir(variables.TempDir)
        if args.background:
            functions.set_background(args.background)
        functions.set_theme(args.theme)
    
def list_themes(args):
    functions.print_theme_list()
def list_colors(args):
    functions.print_color_list()
def backup_update(args):
    functions.backup_update()
def backup_restore(args):
    functions.backup_restore()
def extract_default_theme(args):
    functions.extract_default_theme()
def show_manual(args):
    functions.show_manual(args.prog)
def show_examples(args):
    functions.show_examples(args.prog)
def print_help(args):
    parser.print_help()

# Argument Parser Definition
parser = argparse.ArgumentParser(description='set GDM theme and background'
                                , epilog="run '%(prog)s subcommand --help' for help about a specific subcommand"
                                , usage='%(prog)s [-h] subcommand {options}'
                                )
# AskPass Option
parser.add_argument('-a','--askpass', default='sudo', help='use a different program for elevated privilages')
parser.set_defaults(func=print_help)
# SubParsers
subparsers = parser.add_subparsers(title='subcommands', metavar=None, prog=parser.prog)
desc='set theme and/or background'
parser_set = subparsers.add_parser(name='set', aliases=['s'], help=desc, description=desc)
desc='list installed themes'
parser_list = subparsers.add_parser(name='list', aliases=['l'], help=desc, description=desc)
desc='list acceptable background color names'
parser_list_colors = subparsers.add_parser(name='list-colors', aliases=['lc'], help=desc, description=desc)
desc='extract default theme'
parser_extract = subparsers.add_parser(name='extract', aliases=['x'], help=desc, description=desc)
desc='manage backup of default theme'
parser_backup = subparsers.add_parser(name='backup', aliases=['b'], help=desc, description=desc)
desc='show manual page'
parser_manual = subparsers.add_parser(name='manual', aliases=['m'], help=desc, description=desc)
desc='describe some example commands'
parser_examples = subparsers.add_parser(name='examples', aliases=['e'], help=desc, description=desc)

# Arguments to 'set' subcommand
parser_set_arggroup = parser_set.add_mutually_exclusive_group(required=True)
parser_set_arggroup.add_argument('-r', '--re-apply', action='store_true', help='re-apply the same theme and background')
parser_set_arggroup.add_argument('-b', '--background', dest='opt_background', metavar='BACKGROUND', help='change background only')
parser_set_arggroup.add_argument("theme", nargs='?', help='name of GDM theme', metavar='theme', choices=ThemeList)
parser_set.add_argument('background', nargs='?', help='background image/color')

# Arguments to 'backup' subcommand
subparsers_backup = parser_backup.add_subparsers(required=True)
desc='update backup of default theme'
parser_backup_update = subparsers_backup.add_parser(name='update', aliases=['u'], help=desc, description=desc)
desc='restore default theme from backup'
parser_backup_restore = subparsers_backup.add_parser(name='restore', aliases=['r'], help=desc, description=desc)

# Arguments to 'extract' subcommand
parser_extract.add_argument('dir', nargs='?', help='extract to this directory')
parser_extract.add_argument('theme', nargs='?', metavar='theme', help='theme to extract (possible values: default,distro-default)', choices=['default', 'distro-default'])

# Set Default Functions
parser_set.set_defaults(func=set_theme)
parser_list.set_defaults(func=list_themes)
parser_list_colors.set_defaults(func=list_colors)
parser_extract.set_defaults(func=extract_default_theme)
parser_backup_update.set_defaults(func=backup_update)
parser_backup_restore.set_defaults(func=backup_restore)
parser_manual.set_defaults(func=show_manual)
parser_examples.set_defaults(func=show_examples)

# Finally, parse arguments
args = parser.parse_args()
# Set Program Name as 'prog' member of args namespace
setattr(args, 'prog', parser.prog)
# Run associated function
args.func(args)
# Run commands that need elevated privilages
functions.elevated_commands_list.run()
