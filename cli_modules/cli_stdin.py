from cli_modules.ln_autocompl import completer_init, pair_completer
from copy import deepcopy
from sys import stdout


def input_opts_x_nums(opts_d:dict, max_n:int, cli_hub:bool=True, forbid_chars_after_sharp:list=None) -> tuple:

    hold_d: dict = deepcopy(opts_d)
    opts_list: list = []
    for opt in opts_d:
        if opt == '#': opts_list.append(opt)
        elif not opt.endswith(' '): opts_list.append(opt + ' ')
        else: opts_list.append(opt)

    completer_init(opts_list)

    nums: list = []
    warning: str = ''

    while True:
        opts_d: dict = deepcopy(hold_d)
        cli_hub: str = (f" {warning}\n{[i for i in list(opts_d)]}\n > " if cli_hub else f" {warning}\n > ")
        cli_input: str = input(cli_hub)
        warning: str = ''
        continue_: bool = False
        for opt in list(opts_d):
            if cli_input.count(opt) > 1:
                warning = f" [[ERR] keyword '{opt}' two times matched]"
                continue_ = True; break
            if opt in cli_input:
                if opt in opts_d or opt[:-1] in opts_d:
                    opt = (opt[:-1] if opt not in opts_d else opt)
                    if opt == '#':
                        sharp_index = cli_input.index(opt)
                        cont = cli_input[sharp_index + 1:]
                        if forbid_chars_after_sharp:
                            for char in forbid_chars_after_sharp:
                                if char in cont:
                                    warning = f" [[ERR] forbidden char matched '{char}']"; continue_ = True; break
                        opts_d[opt] = cont
                        cli_input = cli_input[:sharp_index]
                        continue
                    elif type(opts_d[opt]) is bool: opts_d[opt] = opts_d[opt] ^ True
                    elif type(opts_d[opt]) is list: nums = [i for i in range(opts_d[opt][0])]
                    elif type(opts_d[opt]) is str:
                        print(opts_d[opt], file=stdout)
                        continue_ = True
                        break

                cli_input = cli_input.replace(opt, '')
            cli_input = cli_input.replace(opt, '')

        if continue_: continue
        if len(nums) == 0:
            try:
                cli_input_splt = cli_input.split()
                for n, num in enumerate(cli_input_splt):
                    if num != '' and num != 0:
                        if '-' in num:
                            e = None
                            if not num.startswith('-') and not num.endswith('-'):
                                s, e = num.split('-')
                            elif num == '-':
                                s, e = nums.pop(-1)+1, cli_input_splt.pop(n+1)
                            elif num.startswith('-'):
                                s, e = nums.pop(-1)+1, num.split('-')[-1].replace(' ', '')
                            elif num.endswith('-'):
                                s, e = num.split('-')[0].replace(' ', ''), cli_input_splt.pop(n+1)
                            if int(e)-1 in range(max_n):
                                nums += [i-1 for i in range(int(s), int(e)+1)]
                            else: warning = f" [[ERR] '{e}' not in range '{max_n}'"; continue_ = True; break
                        elif int(num)-1 in range(max_n): nums += [int(num) - 1]
                        else: warning = f" [[ERR] '{num}' not in range '{max_n}'"; continue_ = True; break

                if continue_: continue
            except Exception as e:
                warning = f" [[ERR] cast raises '{e}']"
                continue
        return nums, opts_d


def input_stand_alone_x_args(opts_d:dict, stand_alone_x_args:list, cli_hub:bool=True, check_match:bool=True) -> dict:

    if type(stand_alone_x_args[0][0]) == list:
        for pairs in stand_alone_x_args:
            for n, opt in enumerate(pairs[0]): pairs[0][n] = (opt + ' '
                                                              if not opt.endswith(' ')
                                                              else opt)
        pair_completer(stand_alone_opt_x_args1=stand_alone_x_args[0], stand_alone_opt_x_args2=stand_alone_x_args[1])
    else:
        for n, opt in enumerate(stand_alone_x_args[0]): stand_alone_x_args[0][n] = (opt + ' '
                                                                                    if not opt.endswith(' ')
                                                                                    else opt)
        pair_completer(stand_alone_x_args)

    warning = ''
    opts_list = list(opts_d)
    opts_list.sort(key=str.__len__, reverse=True)

    while True:

        cli_hub: str = (f" {warning}\n{[i for i in opts_list] + ['exit']}\n > " if cli_hub else f" {warning}\n > ")
        cli_input: str = input(cli_hub)
        if cli_input == 'exit': return None
        matched: bool = False
        continue_: bool = False
        for opt in opts_list:
            if cli_input.startswith(opt):
                if type(opts_d[opt]) == str: print(opts_d[opt], file=stdout); continue_ = True; break
                opts_d[opt] = cli_input.replace(opt, '', 1); matched = True; break
        if continue_: continue
        if check_match and not matched:
            splt_inp = cli_input.split()
            if len(splt_inp) < 1: warning = f" [[ERR] no input count]"; continue
            warning = f" [[ERR] no match for '{splt_inp[0]}']"; continue
        return opts_d
