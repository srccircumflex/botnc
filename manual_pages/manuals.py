
SLASH: str = '/'
path: str = ''
folder: str = f'{SLASH}manual_pages'

def manual_f(file:str, companion:str=None, split_arg:str= '#' * 90, companions:tuple=('--help', '-h'),
             exiting:bool=False, printing:bool=False):

    from sys import stdout, exit
    cont: str = ""
    if file:
        with open(file, "r") as f:
            if companion:
                fl = f.read().split(split_arg)
                for i in range(len(fl)):
                    if companion == companions[i]: cont = fl[i]
            else:
                cont = f.read()
    if printing: print(cont, file=stdout)
    if exiting: exit()
    return cont


def CLI_COLLECT(): return manual_f(f'{path}{folder}{SLASH}cli_collect')


def GEN_EXPR_CLI(): return manual_f(f'{path}{folder}{SLASH}gen_expr_cli')


def BOTNC_MAIN(comp): manual_f(file=f'{path}{folder}{SLASH}botnc', companion=comp, exiting=True,
                               companions=('--help', '-h', '--help-json', '--help-c'), printing=True)


def CLI_ENV(): return manual_f(f'{path}{folder}{SLASH}table')


def FORENSIC_DELETE(): return manual_f(f'{path}{folder}{SLASH}forensic_delete')
