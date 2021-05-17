#! /bin/python3

script_path: str = "...."  #

import sys

if sys.platform in ('win32', 'cygwin'): SLASH: str = '\\'
else: SLASH: str = '/'

if script_path.endswith(SLASH): script_path = script_path[:-len(SLASH)]
sys.path.append(script_path)

from manual_pages import manuals
from botnc_lib import Builder, Interfaces
from botnc_main import default_kw_args, cli_env, run_cmd
from ast import literal_eval
from getopt import getopt, GetoptError

manuals.path = script_path
manuals.SLASH = SLASH
Builder.SLASH = SLASH
Interfaces.SLASH = SLASH
default_kw_args.SLASH = SLASH

short_opts:str = "t:lM:C:P:m:k:c:vh"

long_opts:list = ['top=', 'follow-links',
                  'map-p-rex=', 'map-f-rex=', 'map-p-reference-off', 'map-or-operand', 'map-rex-i-off',
                  'collect-f-rex=', 'collect-f-rex-i-off', 'collect-empty-too',
                  'preserve-p-rex=', 'preserve-p-repl=', 'preserve-p-sec-rex=', 'preserve-p-at-rex=',
                  'preserve-p-at-sec-rex=', 'preserve-f-rex=', 'preserve-f-repl=', 'preserve-f-sec-rex=',
                  'preserve-f-at-rex=', 'preserve-f-at-sec-rex=',
                  'enable-p-preserve', 'enable-f-preserve',
                  'map-json=', 'collect-json=', 'preserve-json=', 'main-json=',
                  'key-for-table-entry=',
                  'c-command=', 'c-inspect-test', 'c-inspect-test-all', 'c-clean-off',
                  'help', 'help-json', 'help-c']

walkers_top:str = None
follow_links:bool = False
table_entry:str = False
command_count:bool = False
botnc_cmd:str = ""
test_rex_result:bool = False
verbose_test:bool = False
cmd_autoclean:bool = True
preserve_json:dict = None


def read_opt():

    def json_parse(opt_:str, arg_:str):

        global preserve_json

        try:
            arg_json = literal_eval(arg_)
        except Exception as e:
            exit(f" [[ERR] json_parse raises '{e}']")
        if opt_ in ('-M', '--map-json'): default_kw_args.collect_map_kwargs = arg_json
        elif opt_ in ('-C', '--collect-json'): default_kw_args.collect_f_kwargs = arg_json
        elif opt_ in ('-P', '--preserve-json'): preserve_json = arg_json
        elif opt_ in ('-m', '--main-json'):
            if 'map_kwargs' in arg_json: default_kw_args.collect_map_kwargs = arg_json['map_kwargs']
            if 'collect_kwargs' in arg_json: default_kw_args.collect_f_kwargs = arg_json['collect_kwargs']
            if 'preserve_kwargs' in arg_json: preserve_json = arg_json['preserve_kwargs']

    def mk_preserve_json(key:int, arg_:str, index_:list):

        global preserve_json

        if preserve_json is None: preserve_json = {}
        if key not in preserve_json: preserve_json[key] = [['', ''],['']]
        if len(preserve_json[key][index_[0]]) < index_[1] + 1: preserve_json[key][index_[0]].append(' ')
        preserve_json[key][index_[0]][index_[1]] = arg_

    global walkers_top, follow_links, botnc_cmd, table_entry, cmd_autoclean, test_rex_result, verbose_test
    global preserve_json, command_count

    try:
        opts, args = getopt(sys.argv[1:], short_opts, long_opts)
    except GetoptError as e:
        exit(f"{e}\n\n{short_opts}\n{long_opts}")

    for opt, arg in opts:
        if opt in ('--top', '-t'): walkers_top = arg
        elif opt in ('--follow-links', '-l'): follow_links = True
        elif opt == '--map-p-rex': default_kw_args.collect_map_kwargs[0] = arg
        elif opt == '--map-f-rex': default_kw_args.collect_map_kwargs[1] = arg
        elif opt == '--map-p-reference-off': default_kw_args.collect_map_kwargs.__delitem__('use_match_reference')
        elif opt == '--map-or-operand': default_kw_args.collect_map_kwargs['operand'] = 'or'
        elif opt == '--map-rex-i-off': default_kw_args.collect_map_kwargs['ignore'] = False
        elif opt == '--collect-f-rex': default_kw_args.collect_f_kwargs[1] = arg
        elif opt == '--collect-f-rex-i-off': default_kw_args.collect_f_kwargs['ignore'] = False
        elif opt == '--collect-empty-too': default_kw_args.collect_f_kwargs['empty_too'] = True
        elif opt == '--preserve-p-rex': mk_preserve_json(0, arg, [0, 0])
        elif opt == '--preserve-p-repl': mk_preserve_json(0, arg, [0, 1])
        elif opt == '--preserve-p-sec-rex': mk_preserve_json(0, arg, [0, 2])
        elif opt == '--preserve-p-at-rex': mk_preserve_json(0, arg, [1, 0])
        elif opt == '--preserve-p-at-sec-rex': mk_preserve_json(0, arg, [1, 1])
        elif opt == '--preserve-f-rex': mk_preserve_json(1, arg, [0, 0])
        elif opt == '--preserve-f-repl': mk_preserve_json(1, arg, [0, 1])
        elif opt == '--preserve-f-sec-rex': mk_preserve_json(1, arg, [0, 2])
        elif opt == '--preserve-f-at-rex': mk_preserve_json(1, arg, [1, 0])
        elif opt == '--preserve-f-at-sec-rex': mk_preserve_json(1, arg, [1, 1])
        elif opt == '--enable-p-preserve': mk_preserve_json(0, '', [1, 0])
        elif opt == '--enable-f-preserve': mk_preserve_json(1, '', [1, 0])
        elif opt in ('--map-json', '--collect-json', '--preserve-json', '--main-json',
                     '-M', '-C', '-P', '-m'): json_parse(opt, arg)
        elif opt in ('--key-for-table-entry', '-k'): table_entry = arg
        elif opt in ('--c-command', '-c'): botnc_cmd = arg; command_count = True
        elif opt in ('--c-inspect-test', '-v'): test_rex_result = True; command_count = True
        elif opt == '--c-inspect-test-all': verbose_test = True; command_count = True
        elif opt == '--c-clean-off': cmd_autoclean = False; command_count = True
        elif opt in ('-h', '--help', '--help-json', '--help-c'): manuals.BOTNC_MAIN(opt)


def main():

    global walkers_top, follow_links, botnc_cmd, table_entry, cmd_autoclean, test_rex_result
    global verbose_test, command_count

    read_opt()

    if command_count:
        run_cmd.main(botnc_cmd, walkers_top, follow_links, None, None, preserve_json,
                     cmd_autoclean, test_rex_result, verbose_test)
    else:
        cli_env.main(walkers_top, follow_links, None, None, preserve_json, table_entry)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()


if __name__ == "botnc":
    try:
        walkers_top = input(" WALK_TOP: ")
        follow_links = (True if input(" Follow Links[?] ") in ('y', 'Y', 'yes', 'Yes') else False)
        main()
    except Exception as e:
        exit(f" [[ERR] main raises '{e}']")
    except KeyboardInterrupt:
        pass
