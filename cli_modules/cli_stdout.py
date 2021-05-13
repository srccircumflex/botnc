from os import get_terminal_size
from sys import stdout


def print_cli_format(content:list, enum:bool=False, enum_symbol:str= "", columns:int=4,
                     central_head_ln:str=None, attachment:str= "", begin:str= "", end_hl:str= "\n",
                     lazy_columns:bool=False):

    terminal_columns: int = get_terminal_size()[0]
    q_terminal_columns: int = terminal_columns // columns
    count: int = 0
    central_head_ln_: str = f"{begin}{attachment} {central_head_ln} {attachment}"
    if central_head_ln: (print(f"{' ' * ((columns * q_terminal_columns - len(central_head_ln_)) // 2)}"
                               f"{central_head_ln_}" + end_hl, file=stdout) if len(central_head_ln_)
                                                                               <= columns * q_terminal_columns
                         else print(begin + central_head_ln + end_hl, file=stdout))
    line: str = ""
    for n, c in enumerate(content):
        symbol_: str = (f"{n+1}{enum_symbol}" if enum else enum_symbol)
        if count == columns: print(line, file=stdout); line = ""; count = 0
        c: str = symbol_ + c + ' '
        while '\t' in c:
            tap_p = c.index('\t')
            c = c[:tap_p] + ' ' * (4 - (len(c[:tap_p]) % 4)) + c[tap_p + 1:]
        c_len = len(c)
        if c_len >= terminal_columns:
            if line != "": print(line, file=stdout); line = ""; count = 0
            print(c, file=stdout); continue
        if c_len <= q_terminal_columns: line += f"{c}{' '*(q_terminal_columns-c_len)}"; count += 1; continue
        elif lazy_columns:
            if line != "": print(line, file=stdout); line = ""; count = 0
            print(c, file=stdout); continue
        if c_len > q_terminal_columns*(columns - count): print(line, file=stdout); line = ""; count = 0
        for mulp in range(1, columns - count + 1):
            if c_len <= q_terminal_columns*mulp:
                line += f"{c}{' '*(q_terminal_columns*mulp-c_len)}"; count += mulp; break
    if line != "": print(line, file=stdout)


def gen_cli_table_ln(head:list, reserved_columns:dict, over_head:str=None, cut_begin:list=None,
                     alternate_o:list=None):

    if over_head: print_cli_format([], central_head_ln=over_head, end_hl='')

    terminal_columns: int = get_terminal_size()[0]
    terminal_columns_perC: int = round(terminal_columns/100)
    columns_sum: int = 0

    for column in reserved_columns:
        column_size: int = round(reserved_columns[column]*terminal_columns_perC)
        reserved_columns[column] = column_size
        columns_sum += column_size

    while columns_sum < terminal_columns:
        for column in reserved_columns:
            reserved_columns[column] += 1
            columns_sum += 1
    while columns_sum > terminal_columns:
        for column in reserved_columns:
            if reserved_columns[column] <= 2: continue
            if columns_sum == terminal_columns: break
            reserved_columns[column] -= 1
            columns_sum -= 1

    def print_ln(cont:list):
        ln = ""
        for n, c in enumerate(cont):
            while '\t' in c:
                tap_p = c.index('\t')
                c = c[:tap_p] + ' ' * (4 - (len(c[:tap_p]) % 4)) + c[tap_p + 1:]
            while len(c) > reserved_columns[n]-1:
                if cut_begin and n in cut_begin:
                    c = c[1:]
                    if len(c) == reserved_columns[n]-1: c = '…' + c[1:]
                elif alternate_o and n in alternate_o: print(f"{c} ×××", file=stdout); c = '×××'
                else:
                    c = c[:-1]
                    if len(c) == reserved_columns[n]-1: c = c[:-1] + '…'
            while len(c) < reserved_columns[n]-1: c += ' '
            ln += c + ' '
        print(ln, file=stdout)

    print_ln(head)

    while True:
        content: list = yield
        print_ln(content)


def print_2D_map_list(_map_:list, exclude_f:bool=False, nums:list=None, sub_hl:str=None, begin_hl=None):
    if exclude_f:
        print_cli_format([i[0] for i in _map_], enum=True, enum_symbol='\t:', columns=1, lazy_columns=True)
    else:
        attach = ("__" if not sub_hl else "")
        end_hl = ('\n' if not sub_hl else sub_hl)
        begin_hl = ("" if not begin_hl else begin_hl)
        for n in range(len(_map_)):
            if nums and n+1 not in nums: continue
            print_cli_format(_map_[n][1], central_head_ln=_map_[n][0], attachment=attach, end_hl=end_hl, begin=begin_hl)
