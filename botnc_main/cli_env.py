#! /bin/python3

from os import walk
from sys import stdout
from threading import Thread
from botnc_lib.Builder import edit_d, DeCompiler, CmdBuilder, mk_rex_walk_map, fork_base_d, auto_clean
from botnc_lib.Interfaces import inspect, augment_walk_map, cli_collect, botnc_dict_cliT, ForensicDelete
from botnc_lib.Handler import watch_on_q
from manual_pages.manuals import CLI_ENV
from cli_modules.cli_stdin import input_stand_alone_x_args
from botnc_main import default_kw_args


def main(walker_top:str=None, follow_links:bool=False,
         collect_map_kwargs:dict=None,
         collect_f_kwargs:dict=None,
         preserve_kwargs:dict=None,
         cli_table_entry:str=False):

    walker_top:str = default_kw_args.get_top(walker_top)
    if not collect_map_kwargs: collect_map_kwargs:dict = default_kw_args.collect_map_kwargs
    if not collect_f_kwargs: collect_f_kwargs:dict = default_kw_args.collect_f_kwargs

    if cli_table_entry:
        walk_g = walk(walker_top, followlinks=follow_links)
        walk_map:list = mk_rex_walk_map(walk_g, collect_map_kwargs, collect_f_kwargs)
        if preserve_kwargs:
            base_d:dict = augment_walk_map(walk_map, preserve_kwargs, key=cli_table_entry, cli=False)
        else:
            base_d:dict = edit_d(walk_map, cli_table_entry)
    else:
        if not preserve_kwargs: preserve_kwargs:dict = default_kw_args.preserve_kwargs
        base_d:dict = cli_collect(walker_top, follow_links, collect_map_kwargs, collect_f_kwargs, preserve_kwargs)

    forked_d:dict = botnc_dict_cliT(base_d)
    compiler = DeCompiler(forked_d)

    forensic = ForensicDelete(forked_d)
    aut_cmpl_pairs:list = [[['autoclean', 'forensic', 'inspect'], []], [['#'], []]]
    aut_cmpl_pairs:list = compiler.compile_opts(aut_cmpl_pairs)

    cmd_builder = CmdBuilder(out_q=True)
    q = cmd_builder.out_q
    sub_cmd_thread = Thread(target=watch_on_q, kwargs={'q': q})
    sub_cmd_thread.start()

    cmd_used_kys:list = None
    gate:bool = False

    while True:
        try:
            opts:dict = {'autoclean': None, 'forensic': None, 'inspect': None, '#': None, 'help': CLI_ENV()}
            if gate: botnc_dict_cliT(base_d, cmd_used_kys, forked_d)
            else: gate = True
            input_d:dict = input_stand_alone_x_args(opts, aut_cmpl_pairs)
            if not input_d: q.put(None); exit(' [[FINAL] exit]')
            for k in input_d:
                if input_d[k] is not None:
                    inp_spl: list = input_d[k].split()
                    if k == 'autoclean':
                        if len(inp_spl) == 0:
                            auto_clean(forked_d)
                        else:
                            auto_clean(forked_d, inp_spl)
                        gate = False
                    elif k == 'forensic':
                        if len(inp_spl) == 0:
                            forensic.main(forked_d)
                        else:
                            forensic.main(forked_d, inp_spl)
                    elif k == 'inspect':
                        if len(inp_spl) == 0:
                            inspect(forked_d, empty_too=True)
                        else:
                            inspect(forked_d, inp_spl, empty_too=True)
                    elif k == '#':
                        print()
                        pre_comp_A, cmd_used_kys = compiler.decompile_args(input_d[k], base_d)
                        if pre_comp_A: cmd_builder.main(pre_comp_A)
                        else: continue

        except EOFError:
            q.put(None)
            exit(' [[FINAL] EOF]')

        except KeyboardInterrupt:
            print("^C", file=stdout)

        except Exception as e:
            print(f" [[ERR] {e}", file=stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
