from copy import deepcopy
from queue import Queue
from re import search, sub, Pattern, IGNORECASE, compile
from sys import stdout
from botnc_lib.Handler import MakeDir
from botnc_lib.Handler import get_all_until_iteration as get_all

SLASH: str = '/'

class CmdBuilder:

    def __init__(self, ad_per_part:str= '', out_q:bool=False, out_collect:bool=False):
        self.ad_per_part:str = ad_per_part
        self.o_q: bool = False
        if out_q:
            self.out_q = Queue()
            self.o_q = True
        self.c_o:bool = False
        if out_collect:
            self.c_out:list = []
            self.c_o = True

    def build(self, build_array:list, i_positions:list):

        j:int = 0
        for p in range(len(build_array[i_positions[0]])):
            cmd_:str = ""
            for i in i_positions:
                for prt_ in build_array[j:i]: cmd_ += prt_ + self.ad_per_part
                if build_array[i][p]: cmd_ += build_array[i][p] + self.ad_per_part
                else: cmd_ = None; break
                j = i+1
            if cmd_ and j-1 < len(build_array):
                for prt_ in build_array[j:]: cmd_ += prt_ + self.ad_per_part
            j = 0
            if cmd_:
                if self.o_q: self.out_q.put(cmd_)
                if self.c_o: self.c_out.append(cmd_)

    def main(self, build_array):

        i_positions:list = []
        m_positions:list = []
        ii_positions:list = []
        a:int = 0
        m:int = 0

        for n, i in enumerate(build_array):
            n = n + m + a
            if type(i) == list:
                if len(i) > 1 and type(i[0]) == str and type(i[1]) == list:
                    m_positions.append(n)
                    i_positions.append(n + 1)
                    m += 1
                    if len(i) == 4:
                        i_positions.append(n + 3)
                        a += 2
                elif len(i) > 0 and type(i[0]) == list:
                    ii_positions.append(n - m - a)
                    if len(i[0]) > 1 and type(i[0][0]) == str and type(i[0][1]) == list:
                        m_positions.append(n)
                        i_positions.append(n + 1)
                        m += 1
                        if len(i[0]) == 4:
                            i_positions.append(n + 3)
                            a += 2
                    else:
                        i_positions.append(n)
                elif type(i) == list:
                    i_positions.append(n)

        if len(ii_positions) > 0:
            hold_build_A = deepcopy(build_array)
            for i in range(len(build_array[ii_positions[0]])):
                build_array = deepcopy(hold_build_A)
                for j in ii_positions:
                    build_array[j] = build_array[j][i]
                for m in m_positions:
                    build_array = build_array[:m] + build_array[m] + build_array[m + 1:]
                self.build(build_array, i_positions)

        elif len(m_positions) > 0:
            for m in m_positions:
                build_array = build_array[:m] + build_array[m] + build_array[m + 1:]
            self.build(build_array, i_positions)

        elif len(i_positions) < 1:
            cmd_ = ""
            if self.o_q: self.out_q.put(cmd_.join(build_array))
            if self.c_o: self.c_out.append(cmd_.join(build_array))

        else:
            self.build(build_array, i_positions)

        if self.c_o: return self.c_out


def edit_d(list_content:list, d_key:str, dict_:dict={}) -> dict:
    if d_key in dict_: dict_[d_key] += list_content
    else: dict_[d_key] = list_content
    return dict_


def mk_rex_walk_map(walk_gen, collect_map_kwargs:dict, collect_f_kwargs:dict=None, enum_stdout:int=False):

    map_:list = []

    sub_cache:dict = None
    if 'use_match_reference' in collect_map_kwargs and collect_map_kwargs['use_match_reference'] in (0,1):
        sub_cache = {collect_map_kwargs['use_match_reference'] : ''}
        collect_map_kwargs.__delitem__('use_match_reference')

    operand:str = 'and'
    if 'operand' in collect_map_kwargs and collect_map_kwargs['operand'] in ('and', 'or'):
        operand = collect_map_kwargs['operand']
        collect_map_kwargs.__delitem__('operand')

    ignore:list = [True, True]
    if 'ignore' in collect_map_kwargs and collect_map_kwargs['ignore'] in (0,1):
        ignore[0] = collect_map_kwargs['ignore']
        collect_map_kwargs.__delitem__('ignore')

    for k in list(collect_map_kwargs):
        if ignore[0]: collect_map_kwargs[k] = (compile(collect_map_kwargs[k], flags=IGNORECASE)
                                               if not type(collect_map_kwargs[k]) == Pattern
                                               else collect_map_kwargs[k])
        else: collect_map_kwargs[k] = (compile(collect_map_kwargs[k]) if not type(collect_map_kwargs[k]) == Pattern
                                       else collect_map_kwargs[k])

    operand:str = (None if len(list(collect_map_kwargs)) < 2 else operand)

    empty_too:bool = False
    if collect_f_kwargs:
        if 'empty_too' in collect_f_kwargs:
            empty_too = collect_f_kwargs['empty_too']
            collect_f_kwargs.__delitem__('empty_too')
        if 'ignore' in collect_f_kwargs and collect_f_kwargs['ignore'] in (0, 1):
            ignore[1] = collect_f_kwargs['ignore']
            collect_f_kwargs.__delitem__('ignore')
        for k in collect_f_kwargs:
            if ignore[1]: collect_f_kwargs[k] = (compile(collect_f_kwargs[k], flags=IGNORECASE)
                                                 if not type(collect_f_kwargs[k]) == Pattern
                                                 else collect_f_kwargs[k])
            else: collect_f_kwargs[k] = (compile(collect_f_kwargs[k]) if not type(collect_f_kwargs[k]) == Pattern
                                         else collect_f_kwargs[k])

    enum:int = 0
    while True:
        try:
            walk_val:tuple = get_all(walk_gen)
            if not walk_val: return map_
            walk_map = [[walk_val[0]], walk_val[2]]
            op_gate = None
            second_search = list(collect_map_kwargs)[-1]
            for k in collect_map_kwargs:
                if operand == 'and' and k == list(collect_map_kwargs)[-1] and op_gate not in (0, 1): break
                for n, f in enumerate(walk_map[k]):
                    if sub_cache and k in sub_cache and sub_cache[k] != '':
                        if sub_cache[k] in f:
                            if k == second_search: op_gate = (True if op_gate in (0,1) else False)
                            else: op_gate = False
                        else: sub_cache[k] = ''
                    if search(collect_map_kwargs[k], f):
                        if k == second_search: op_gate = (True if op_gate in (0, 1) else False)
                        else: op_gate = False
                        if sub_cache and k in sub_cache: sub_cache[k] = f
            if collect_f_kwargs:
                for k in collect_f_kwargs:
                    for n, f in enumerate(walk_map[k]):
                        if not search(collect_f_kwargs[k], f): walk_map[k][n] = 0
                    while 0 in walk_map[k]: walk_map[k].remove(0)
            if not empty_too and list() in walk_map: continue
            if (operand == 'and' and op_gate) or (operand != 'and' and op_gate in (0,1)):
                map_.append([walk_map[0][0],walk_map[1]])
                if enum_stdout:
                    enum += 1; print(f"{enum}\t:{walk_map[0][0]}", file=stdout)
        except KeyboardInterrupt:
            return map_


def rex_manipulate(_map:list, rex_args:list, second_reference:list=None, slash_safe_mode:bool=True) -> list:

    if slash_safe_mode and ((rex_args[0].startswith((f'^{SLASH}', SLASH)) and not rex_args[1].startswith(SLASH))
                            or (rex_args[0].endswith((f'{SLASH}$', SLASH)) and not rex_args[1].endswith(SLASH))
                            and len(rex_args[0]) > 1):
        if input(' [WARNING] if match: modify path-separators\n <confirmed> [ y | n ] ') not in ('Y', 'y', 'yes', 'ok'):
            return _map

    if type(_map) != list: _map:list = [_map]

    for n in range(len(_map)):
        try:
            continue_ = (True if second_reference else False)
            if second_reference:
                if len(second_reference) == 3:
                    if type(second_reference[2]) != list: second_reference[2] = [second_reference[2]]
                    for i in second_reference[2]:
                        if search(second_reference[1], i):
                            if search(second_reference[0], search(second_reference[1], i).group()):
                                continue_ = False; break
                elif len(second_reference) == 2:
                    if type(second_reference[1]) != list: second_reference[1] = [second_reference[1]]
                    for i in second_reference[1]:
                        if search(second_reference[0], i): continue_ = False; break
                else: print(" [[ERR] second_reference range not in (2,3)]")
            if continue_: continue
            if len(rex_args) == 3:
                if search(rex_args[2], _map[n]):
                    _map[n] = sub(rex_args[2], sub(rex_args[0], rex_args[1], search(rex_args[2], _map[n]).group()),
                                  _map[n])
            elif len(rex_args) == 2:
                _map[n] = sub(rex_args[0], rex_args[1], _map[n])
            else: print(" [[ERR] rex_args range not in (2,3)]")
        except Exception as e:
            print(f" [[ERR] rex_manipulate raises '{e}']")

    return _map


def re_escape(array:list):

    import re
    re._special_chars_map = {i: '\\' + chr(i) for i in b' \\^!"$&()=?`*\'<>|{[]},;:\t\n\r\v\f'}
    if type(array) != list: array:list = [array]
    return [re.escape(i) for i in array]


def fork_base_d(base_d:dict) -> dict:

    forked_d:dict = {}
    for k in base_d:
        for n, c in enumerate(base_d[k]):
            if len(c) == 4:
                forked_d[f"{k}.{n+1}.a"] = [base_d[k][n][2], base_d[k][n][3]]
            forked_d[f"{k}.{n+1}"] = [base_d[k][n][0], base_d[k][n][1]]
    return forked_d


def auto_clean(forked_d:dict, key_list:list=None):

    def cleaner(key:str):
        if key + '.a' in forked_d:
            cont = deepcopy(forked_d[key][1])
            for c in cont:
                if c in forked_d[key + '.a'][1]:
                    forked_d[key + '.a'][1].remove(c)
                    forked_d[key][1].remove(c)

    if not key_list or len(key_list) == 0:
        for k in forked_d: cleaner(k)
    else:
        for k in key_list:
            if search("\.[0-9]*\.a$", k):
                cleaner(k[1:-2])
            elif search("\.[0-9]*$", k):
                cleaner(k[1:])
            else:
                for ky in forked_d:
                    search_k = search(k + "\.[0-9]*$", ky)
                    if search_k:
                        cleaner(search_k.group()[1:])


class DeCompiler:

    def __init__(self, forked_d:dict):
        self.forked_d: dict = forked_d
        self.used_kys: list = []

    def compile_opts(self, auto_completer_pairs:list) -> list:

        matched:str = False
        for k in self.forked_d:
            if not matched or not search("^" + matched + "\.[0-9]*.a?$", k):
                base_k = sub("\.[0-9]*.a?$", '', k)
                matched = base_k
                auto_completer_pairs[0][1].append('§' + base_k + ' ')
                auto_completer_pairs[1][1].append('§' + base_k + ' ')
                if not search("^" + matched + "\.[0-9]*.a?$", k): matched = False; continue
            auto_completer_pairs[0][1].append('§' + k + ' ')
            auto_completer_pairs[1][1].append('§' + k + ' ')
            auto_completer_pairs[1][1].append('§' + k + '.f ')
            auto_completer_pairs[1][1].append('§' + k + '.p ')

        return auto_completer_pairs

    def decompile_args(self, botnc_cmd:str, base_d:dict=None) -> tuple:

        pre_compiled_cmd:list = []
        pre_compiled_aug:list = []
        input_splt:list = botnc_cmd.split()
        to_escape:str = ""
        do_escape:bool = False

        try:
            for c in input_splt:
                if c == '\\f':
                    if type(pre_compiled_cmd[-1]) == list and \
                            type(pre_compiled_cmd[-1][0]) == str and \
                            pre_compiled_cmd[-1][0].count(SLASH) == 1:
                        for n in range(len(pre_compiled_cmd[-1])):
                            if pre_compiled_cmd[-1][n].startswith(SLASH):
                                pre_compiled_cmd[-1][n] = pre_compiled_cmd[-1][n][len(SLASH):]
                elif c == '\\S':
                    if type(pre_compiled_cmd[-1]) == list:
                        if type(pre_compiled_cmd[-1][0]) == list:
                            for a_map in pre_compiled_cmd[-1]:
                                for n in range(len(a_map[1])):
                                    if len(pre_compiled_cmd[-1][0]) == 4:
                                        if a_map[3][n].endswith(' '): a_map[3][n] = a_map[3][n][:-1]
                                    else:
                                        if a_map[1][n].endswith(' '): a_map[1][n] = a_map[1][n][:-1]
                        else:
                            for n in range(len(pre_compiled_cmd[-1])):
                                if pre_compiled_cmd[-1][n].endswith(' '):
                                    pre_compiled_cmd[-1][n] = pre_compiled_cmd[-1][n][:-1]
                    elif pre_compiled_cmd[-1].endswith(' '): pre_compiled_cmd[-1] = pre_compiled_cmd[-1][:-1]
                elif c == '\\s':
                    if do_escape: to_escape += ' '
                    pre_compiled_cmd.append(' ')
                elif c in ('§', '§§'):
                    if not do_escape:
                        do_escape = True
                    else:
                        p = re_escape(array=[to_escape[:-1]])[0]
                        p = p + ' '
                        if c == '§§':
                            makedir = MakeDir([to_escape[:-1]])
                            makedir.run()
                            p = p[:-1]
                        pre_compiled_cmd.append(p)
                        do_escape = False
                        to_escape = ""
                elif do_escape: to_escape += c + ' '
                elif c.startswith('§'):
                    if c.endswith('.p'):
                        p = re_escape(array=[self.forked_d[c[1:-2]][0]])[0]
                        makedir = MakeDir([self.forked_d[c[1:-2]][0]])
                        makedir.run()
                        pre_compiled_cmd.append(p)
                        (self.used_kys.append(c[1:-2].replace('.a', ''))
                         if not c[1:-2].replace('.a', '') in self.used_kys else None)
                    elif c.endswith('.f'):
                        f_A = [SLASH + f + ' ' for f in re_escape(array=self.forked_d[c[1:-2]][1])]
                        pre_compiled_cmd.append(f_A)
                        (self.used_kys.append(c[1:-2].replace('.a', ''))
                         if not c[1:-2].replace('.a', '') in self.used_kys else None)
                    elif search("\.[0-9]*.a?$", c[1:]):
                        p = re_escape(array=[self.forked_d[c[1:]][0]])[0]
                        makedir = MakeDir([self.forked_d[c[1:]][0]])
                        makedir.run()
                        pre_compiled_cmd.append(p)
                        f_A = [SLASH + f + ' ' for f in re_escape(array=self.forked_d[c[1:]][1])]
                        pre_compiled_cmd.append(f_A)
                        (self.used_kys.append(c[1:].replace('.a', ''))
                         if not c[1:].replace('.a', '') in self.used_kys else None)
                    elif base_d and c[1:] in base_d:
                        for n in range(1, 99999):
                            formated_k = f"{c[1:]}.{n}"
                            if formated_k in self.forked_d:
                                p = re_escape(array=[self.forked_d[formated_k][0]])[0]
                                makedir = MakeDir([self.forked_d[formated_k][0]])
                                makedir.run()
                                f_A = [SLASH + f + ' ' for f in re_escape(array=self.forked_d[formated_k][1])]
                                if formated_k + '.a' in self.forked_d:
                                    pa = re_escape(array=[self.forked_d[formated_k + '.a'][0]])[0]
                                    makedir = MakeDir([self.forked_d[formated_k + '.a'][0]])
                                    makedir.run()
                                    f_Aa = [SLASH + f + ' '
                                            for f in re_escape(array=self.forked_d[formated_k + '.a'][1])]
                                    pre_compiled_aug.append([p, f_A, pa, f_Aa])
                                else:
                                    pre_compiled_aug.append([p, f_A])
                                (self.used_kys.append(formated_k.replace('.a', ''))
                                 if not formated_k.replace('.a', '') in self.used_kys else None)
                            else:
                                pre_compiled_cmd.append(pre_compiled_aug)
                                break
                else:
                    pre_compiled_cmd.append(c + ' ')

        except Exception as e:
            print(f" [[ERR] DeCompiler raises '{e}'", file=stdout)
            return None, None
        else:
            return pre_compiled_cmd, self.used_kys
