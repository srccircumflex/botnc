from os import walk, get_terminal_size
from random import randint
from sys import stdout
from copy import deepcopy
from re import search
from cli_modules.cli_stdout import print_2D_map_list, gen_cli_table_ln, print_cli_format
from cli_modules.ln_autocompl import pair_completer
from botnc_lib.Builder import mk_rex_walk_map, edit_d, rex_manipulate
from manual_pages.manuals import CLI_COLLECT, GEN_EXPR_CLI, FORENSIC_DELETE
from cli_modules.cli_stdin import input_opts_x_nums, edit_buffer

SLASH: str = '/'

def cli_collect(walker_top:str, follow_links:bool, collect_map_kwargs:dict, collect_f_kwargs:dict=None,
                augment_kwargs:dict=None) -> dict:

    augment_kwargs:dict = ({0:['', '', ''], 1:['', '', '']} if not augment_kwargs else augment_kwargs)

    walk_gen:object = walk(walker_top, followlinks=follow_links)
    map_:list = mk_rex_walk_map(walk_gen, collect_map_kwargs, collect_f_kwargs, True)

    base_d:dict = {}

    while len(map_) > 0:
        try:
            nums, opts = input_opts_x_nums({
                'preserve': False,
                'all': [len(map_)],
                'help': CLI_COLLECT(),
                'continue': False,
                '#': None
            }, len(map_), forbid_chars_after_sharp=[' ', '.', '§'])
            if opts['continue']: return base_d
            elif opts['preserve']:
                base_d = augment_walk_map([map_[i] for i in nums], augment_kwargs, key=opts['#'], out_d=base_d,
                                          forbid_chars_in_key=[' ', '.', '§'])
            elif opts['#']:
                map__ = deepcopy(map_)
                base_d = edit_d([map__[i] for i in nums], opts['#'], base_d)
            if opts['preserve'] or opts['#']:
                for n, i in enumerate(nums):
                    map_.__delitem__(i - n)
            for n, f in enumerate(map_):
                print(f"{n+1}\t:{f[0]}", file=stdout)
        except KeyboardInterrupt:
            print("^C", file=stdout)
        except EOFError:
            return base_d
    return base_d


def gen_expr_cli(rex_args:list, second_reference:list=None, slash_safe_mode:bool=True,
                 forbid_chars_after_sharp:list=None) -> tuple:

    def init_pair_completer():

        nonlocal expr_bulk_start, expr_bulk_sep, expr_bulk_end, done_opt, rex_opt, at_opt, syntax_opt, gob_opt
        base_opts: list = [[syntax_opt, 'help', gob_opt], []]
        prep_rex: list = [[rex_opt, at_opt], [
            done_opt, gob_opt,
            # some useful reminders
            expr_bulk_start + expr_bulk_sep + expr_bulk_sep + expr_bulk_end,
            f'{expr_bulk_start}{SLASH}{expr_bulk_sep}{SLASH}···', f'{expr_bulk_sep}{SLASH}*[^{SLASH}]*.${expr_bulk_end}',
            f'{expr_bulk_start}${expr_bulk_sep}···'
        ]]  # ···

        pair_completer(base_opts, prep_rex, selection=False, delims=' \t\n`~!#$%^&*()-=+[{]}\\|;:\'",<>/?')

    expr_bulk_start: str = '<'
    expr_bulk_sep: str = '~'
    expr_bulk_end: str = '>'
    done_opt: str = ' #'
    rex_opt: str = f'rex{expr_bulk_start}'
    at_opt: str = f'@{expr_bulk_start}'
    syntax_opt: str = 'syntax'
    gob_opt: str = f'gob{expr_bulk_start}'

    init_pair_completer()

    cli_loop: bool = True
    cli_loop_i1: bool = False
    key: str = None
    warning: str = ""

    while True:
        gob: bool = False

        pre_args:str = f"{rex_args}{second_reference}{cli_loop}{cli_loop_i1}{gob}"
        opt:str = input(f"{warning}\n[{rex_opt}]:{rex_args};[{at_opt}]:{second_reference}\n"
                        f"'{expr_bulk_start}''{expr_bulk_sep}''{expr_bulk_end}''{done_opt}' ")
        warning:str = ""

        if rex_opt in opt:
            rex_args_ = opt.split(rex_opt)[-1].split(expr_bulk_end)[0].split(expr_bulk_sep)
            if slash_safe_mode and ((rex_args_[0].startswith((f'^{SLASH}', SLASH)) and not rex_args_[1].startswith(SLASH))
                                    or (rex_args_[0].endswith((f'{SLASH}$', SLASH)) and not rex_args_[1].endswith(SLASH)
                                         and rex_args_[0] not in (f'^{SLASH}', SLASH))):
                if input(' [WARNING] refactor path-separators\n <confirmed> [ y | n ] ')\
                        not in ('Y', 'y', 'yes', 'ok'): continue
            rex_args = rex_args_
        if at_opt in opt:
            second_reference = opt.split(at_opt)[-1].split(expr_bulk_end)[0].split(expr_bulk_sep)
        if done_opt in opt:
            done_i_i = opt.index(done_opt)
            cli_loop, cli_loop_i1 = ((False, False) if opt.startswith(done_opt) else (True, True))
            if not opt.endswith(done_opt):
                key_ = opt[done_i_i+len(done_opt):]
                continue_ = False
                if forbid_chars_after_sharp:
                    for i in forbid_chars_after_sharp:
                        if i in key_:
                            warning = f" [[ERR] forbidden char matched '{i}']"
                            continue_ = True; break
                if continue_: continue
                else: key = key_
        if gob_opt in opt:
            gob = True
        if opt.startswith(syntax_opt):
            try:
                opt_split = opt.split(expr_bulk_sep)
                if '' in opt_split[:-1]: raise Exception
                _, expr_bulk_start, expr_bulk_sep, expr_bulk_end, done_opt, _ = opt_split
                init_pair_completer()
            except Exception as e: print(f" [Err] {e}\n {opt_split}\n [i] separator is '{expr_bulk_sep}'")
            continue
        elif opt == 'help' or opt == 'h' or opt == "Help" or opt == 'info' or opt == 'i' or opt == 'Info':
            print(GEN_EXPR_CLI(), file=stdout)
            continue
        elif f"{rex_args}{second_reference}{cli_loop}{cli_loop_i1}{gob}" == pre_args:
            warning = " [WARNING] nothing modified; may use 'help'"

        yield rex_args, second_reference, cli_loop, cli_loop_i1, key, gob


def augment_walk_map(_walk_map:list, kwargs:dict, key:str=None, out_d:dict={}, cli:bool=True,
                     forbid_chars_in_key:list=None) -> dict:

    def map_association_augment(_map:list) -> list:
        nonlocal kwargs, key, cli
        map_: list = deepcopy(_map)
        _map: list = deepcopy(_map)
        kwarg_ks: list = (list(kwargs) if list(kwargs) in ([1], [0], [1, 0], [0, 1]) else
                          exit(f" [[ERR] key err in augment_walk_map: (0 &|| 1)]\n{kwargs}"))
        for k in kwarg_ks:
            if type(kwargs[k]) == bool:
                rex_args: list = ['', '']
                second_reference = None
            else:
                rex_args: list = (kwargs[k][0] if type(kwargs[k][0]) == list else kwargs[k])
                second_reference: list = (kwargs[k][1] if type(kwargs[k][1]) == list else None)

            if cli: cli_gen = gen_expr_cli(rex_args, second_reference, slash_safe_mode=(False if k == 1
                                                                                               else True),
                                           forbid_chars_after_sharp=[' ', '.', '§'])
            cli_gate: bool = True
            cli_i1: bool = False
            first_loop: bool = True
            gob: bool = False
            while cli_gate:
                cli_:bool = (False if cli_i1 else cli)
                for n in range(len(_map)):
                    if k == 0:
                        target_sigh = "→"
                        map_[n][0] = _map[n][0]
                        map_[n][0] = rex_manipulate(map_[n][0], rex_args, ([i for i in second_reference] + [_map[n][1]]
                                                                           if second_reference else None),
                                                    slash_safe_mode=(True if first_loop else False))[0]
                        if gob: map_[n][0] = edit_buffer([map_[n][0]])[0]

                    elif k == 1:
                        target_sigh = "↓"
                        map_[n][1] = deepcopy(_map[n][1])
                        map_[n][1] = rex_manipulate(map_[n][1], rex_args, ([i for i in second_reference]
                                                                           + [[_map[n][0]]]
                                                                           if second_reference else None),
                                                    slash_safe_mode=False)
                        if gob: map_[n][1] = edit_buffer(map_[n][1])

                    if cli_: print_2D_map_list([[_map[n][0], map_[n][1]]],
                                               sub_hl=f"\n  [ {map_[n][0]} ]", begin_hl=f'\n {target_sigh}  ')
                if not cli_: cli_gate = False
                else: rex_args, second_reference, cli_gate, cli_i1, key_, gob = next(cli_gen); key = (key_ if not key
                                                                                                      else key)
                if first_loop: first_loop = False

        for n in range(len(_map)): _map[n] += map_[n]
        if not key:
            warn:str = ""
            while True:
                key_ = input(f" {warn}[set key] ")
                warn = ""
                break_:bool = True
                if forbid_chars_in_key:
                    for char in forbid_chars_in_key:
                        if char in key_:
                            warn = f" [[ERR] forbidden char matched '{char}']"
                            break_ = False; break
                if break_:
                    key = key_
                    break
        return _map

    _map_ = map_association_augment(_walk_map)

    return edit_d(_map_, key, out_d)


def botnc_dict_cliT(base_d:dict, used_kys:list=None, forked_d:dict=None) -> dict:

    print('+' + (' ' * (get_terminal_size()[0] - 2)) + '+', file=stdout)

    cli_ln = gen_cli_table_ln(['[F] _KEY_', '[#]', '[n] [a]', '[.p] _PATH_', '[.f] _FILES_PREVIEW_'],
                              {0: 10, 1: 3, 2: 5, 3: 34, 4: 35},
                              cut_begin=[3, 4])
    next(cli_ln)

    forked_d_:dict = {}
    for k in base_d:
        for n, c in enumerate(base_d[k]):
            if len(c) == 4:
                flag:str = '[a] '
                aug:str = ' .a'
                forked_d_[f"{k}.{n+1}.a"] = [base_d[k][n][2], base_d[k][n][3]]
            else:
                flag:str = '[ ] '
                aug:str = '   '
            if len(c[1]) > 0: fp:str = SLASH + c[1][randint(0, len(c[1])-1)]
            elif forked_d and len(forked_d[f"{k}.{n + 1}"][1]) > 0:
                fp:str = SLASH + forked_d[f"{k}.{n + 1}"][1][randint(0, len(forked_d[f"{k}.{n + 1}"][1]) - 1)]
            else: fp:str = "-- EMPTY --"
            if used_kys and f"{k}.{n+1}" in used_kys: used_flag:str = '[x]'
            else: used_flag:str = '   '
            cli_ln.send([flag + k, used_flag, f".{n+1} {aug}", c[0], fp])
            forked_d_[f"{k}.{n+1}"] = [base_d[k][n][0], base_d[k][n][1]]
    cli_ln.close()

    return forked_d_


def fd_delete(forked_d:dict, k:str, max_i:int, k_a:str=None):

    opts: dict = {'confirmed': False, 'undo': False, 'help': FORENSIC_DELETE()}
    nums, kw_D = input_opts_x_nums(opts, max_i)
    for n, d in enumerate(nums):
        forked_d[k][1].__delitem__(d - n)
        if k_a: forked_d[k_a][1].__delitem__(d - n)
    return kw_D['confirmed'], kw_D['undo']


def fd_printing(k_ll:list, DD:dict):
    from cli_modules.cli_stdout import print_cli_format
    from os import get_terminal_size
    from sys import stdout
    print('–' * get_terminal_size()[0], file=stdout)
    for lk in k_ll:
        print_cli_format(DD[lk][1], central_head_ln=DD[lk][0], begin=f"[{lk}] ",
                         enum=True, enum_symbol=': ')
    print('–' * get_terminal_size()[0], file=stdout)


class ForensicDelete:

    def __init__(self, forked_d:dict, confirm_it:bool=True):

        self.confirm = confirm_it
        self.hold_d = deepcopy(forked_d)

    def main(self, forked_d:dict, k_list:list=None):

        try:
            if not k_list or len(k_list) == 0:
                k_l = list(forked_d)
                for n, k in enumerate(k_l):
                    while True:
                        if search("\.[0-9]*\.a$", k):
                            fd_printing([k, k_l[n + 1]], forked_d)
                            opt_del, opt_undo = fd_delete(forked_d, k, len(forked_d[k][1]), k_l[n + 1])
                            if self.confirm:
                                if opt_del: k_l.__delitem__(n+1); break
                                elif opt_undo:
                                    forked_d[k] = deepcopy(self.hold_d[k])
                                    forked_d[k_l[n + 1]] = deepcopy(self.hold_d[k_l[n + 1]])
                            else: k_l.__delitem__(n+1); break

                        else:
                            fd_printing([k], forked_d)
                            opt_del, opt_undo = fd_delete(forked_d, k, len(forked_d[k][1]))
                            if self.confirm:
                                if opt_del: break
                                elif opt_undo:
                                    forked_d[k] = deepcopy(self.hold_d[k])
                            else: break
            else:
                for k in k_list:
                    k = k[1:]
                    if search("\.[0-9]*\.a$", k):
                        while True:
                            fd_printing([k, k[:-2]], forked_d)
                            opt_del, opt_undo = fd_delete(forked_d, k[:-2], len(forked_d[k][1]), k)
                            if self.confirm:
                                if opt_del: break
                                elif opt_undo:
                                    forked_d[k] = deepcopy(self.hold_d[k])
                                    forked_d[k[:-2]] = deepcopy(self.hold_d[k:-2])
                            else: break
                    elif search("\.[0-9]*$", k):
                        if k + '.a' in forked_d:
                            while True:
                                fd_printing([k + '.a', k], forked_d)
                                opt_del, opt_undo = fd_delete(forked_d, k, len(forked_d[k][1]), k + '.a')
                                if self.confirm:
                                    if opt_del:
                                        if k + '.a' in k_list: k_list.remove(k + '.a')
                                        break
                                    elif opt_undo:
                                        forked_d[k] = deepcopy(self.hold_d[k])
                                        forked_d[k + '.a'] = deepcopy(self.hold_d[k + '.a'])
                                else:
                                    if k + '.a' in k_list: k_list.remove(k + '.a')
                                    break
                        else:
                            while True:
                                fd_printing([k], forked_d)
                                opt_del, opt_undo = fd_delete(forked_d, k, len(forked_d[k][1]))
                                if self.confirm:
                                    if opt_del: break
                                    elif opt_undo: forked_d[k] = deepcopy(self.hold_d[k])
                                else: break
                    else:
                        a = False
                        for DD_k in forked_d:
                            if search(k + "\.[0-9]*\.a", DD_k): a = True; break
                        for n in range(1, 99999):
                            formated_k = f"{k}.{n}"
                            if formated_k in forked_d:
                                while True:
                                    if a:
                                        fd_printing([formated_k + '.a', formated_k], forked_d)
                                        opt_del, opt_undo = fd_delete(forked_d, formated_k,
                                                                      len(forked_d[formated_k][1]), formated_k + '.a')
                                        if self.confirm:
                                            if opt_del: break
                                            elif opt_undo:
                                                forked_d[formated_k] = deepcopy(self.hold_d[formated_k])
                                                forked_d[formated_k + '.a'] = deepcopy(self.hold_d[formated_k + '.a'])
                                        else: break
                                    else:
                                        fd_printing([formated_k], forked_d)
                                        opt_del, opt_undo = fd_delete(forked_d, formated_k, len(forked_d[formated_k][1]))
                                        if self.confirm:
                                            if opt_del: break
                                            elif opt_undo: forked_d[formated_k] = deepcopy(self.hold_d[formated_k])
                                        else: break
                            else: break
        except KeyboardInterrupt:
            print()


def inspect(forked_d:dict, k_list:list=None, empty_too:bool=False):

    def printing(k_l_:list):

        if not empty_too and len(forked_d[k_l_[0]][1]) == 0: return
        print('=' * get_terminal_size()[0], file=stdout)
        for k_ in k_l_:
            print_cli_format(forked_d[k_][1], central_head_ln=forked_d[k_][0], begin=f"[{k_}]", end_hl='')
        print('=' * get_terminal_size()[0], file=stdout)

    try:
        if not k_list or len(k_list) == 0:
            k_l = list(forked_d)
            for n, k in enumerate(k_l):
                if k.endswith('.a'):
                    printing([k, k_l[n + 1]])
                    k_l.__delitem__(n+1)
                else:
                    printing([k])
        else:
            for k in k_list:
                k = k[1:]
                if search("\.[0-9]*\.a$", k):
                    printing([k, k[:-2]])
                elif search("\.[0-9]*$", k):
                    if k + '.a' in forked_d:
                        printing([k + '.a', k])
                        if k + '.a' in k_list: k_list.remove(k + '.a')
                    else:
                        printing([k])
                else:
                    if k + '.1' + '.a' in forked_d:
                        for n in range(1, 99999):
                            formated_k = f"{k}.{n}"
                            if formated_k in forked_d:
                                printing([formated_k + '.a', formated_k])
                            else:
                                break
                    elif k + '.1' in forked_d:
                        for n in range(1, 99999):
                            formated_k = f"{k}.{n}"
                            if formated_k in forked_d:
                                printing([formated_k])
                            else:
                                break
    except KeyboardInterrupt:
        pass
