
SLASH : str = '/'

def get_top(input_:str=None):
    from os import getcwd, environ
    if not input_: return getcwd()
    elif input_ == '/': return input_
    elif input_.endswith(SLASH): input_ = input_[:-len(SLASH)]
    if input_.startswith('~'):
        return environ['HOME'] + input_[1:]
    else: return input_

collect_map_kwargs:dict = {
    0: '',
    1: '',
    'use_match_reference': 0,
    'operand': 'and',
    'ignore': True
}


collect_f_kwargs:dict = {
    1: '',
    'ignore': True,
    'empty_too': False
}


preserve_kwargs:dict = {
    0: [['','',''],['', '']],
    1: [['','',''],['', '']]
}
