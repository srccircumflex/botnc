#! /bin/python3

from os import walk
from threading import Thread
from botnc_lib.Builder import edit_d, DeCompiler, CmdBuilder, mk_rex_walk_map, fork_base_d, auto_clean
from botnc_lib.Interfaces import inspect, augment_walk_map
from botnc_lib.Handler import watch_on_q
from botnc_main import default_kw_args


def main(botnc_cmd:str="",
         walker_top:str=None,
         follow_links:bool=False,
         collect_map_kwargs:dict=None,
         collect_f_kwargs:dict=None,
         preserve_kwargs:dict=None,
         autoclean:bool=True,
         inspect_test:bool=False,
         inspect_empty_too:bool=False
         ):

    walker_top:str = default_kw_args.get_top(walker_top)
    walk_g = walk(walker_top, followlinks=follow_links)

    if not collect_map_kwargs: collect_map_kwargs: dict = default_kw_args.collect_map_kwargs
    if not collect_f_kwargs: collect_f_kwargs: dict = default_kw_args.collect_f_kwargs

    walk_map:list = mk_rex_walk_map(walk_g, collect_map_kwargs, collect_f_kwargs)
    if preserve_kwargs:
        base_d:dict = augment_walk_map(walk_map, preserve_kwargs, '__KEY__-', cli=False)
    else:
        base_d:dict = edit_d(walk_map, '__KEY__-')

    forked_d:dict = fork_base_d(base_d)

    if autoclean:
        auto_clean(forked_d)

    if inspect_test:
        inspect(forked_d, empty_too=inspect_empty_too)
        exit()

    botnc_cmd:str = botnc_cmd.replace(' §§§', ' §__KEY__-')
    cmd_builder = CmdBuilder(out_q=True)
    q = cmd_builder.out_q
    cmd_sub_thread = Thread(target=watch_on_q, kwargs={'q': q})
    cmd_sub_thread.start()
    compiler = DeCompiler(forked_d)

    if ' §__KEY__-.n' in botnc_cmd:
        for n in range(1, 99999):
            hold_botnc_cmd: str = botnc_cmd
            if f'__KEY__-.{n}' not in forked_d: break
            while ' §__KEY__-.n' in botnc_cmd: botnc_cmd = botnc_cmd.replace(' §__KEY__-.n', f' §__KEY__-.{n}')
            pre_compiled, _ = compiler.decompile_args(botnc_cmd, base_d)
            if pre_compiled: cmd_builder.main(pre_compiled)
            botnc_cmd = hold_botnc_cmd
    else:
        pre_compiled, _ = compiler.decompile_args(botnc_cmd, base_d)
        if pre_compiled: cmd_builder.main(pre_compiled)
    q.put(None)
