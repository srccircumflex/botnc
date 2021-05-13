from readline import set_completer, parse_and_bind, set_completer_delims, get_line_buffer
from copy import deepcopy


def completer_init(opts:list=[], args:list=None, keywords:list=None, absolut_opts:list=None,
                   delims:str= ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?', use_IN_req:bool=False, selection:bool=True):

    class Completer(object):

        def __init__(self, options: list, arguments:list=None):

            nonlocal keywords, absolut_opts, use_IN_req, selection

            self.opts_wo_s: list = []
            for p in options:
                self.opts_wo_s.append((p[:-1] if p.endswith(' ') else p))
            self.final_opts: list = absolut_opts
            self.arguments: list = arguments
            self.opts_x_kws: list = deepcopy((options + keywords if keywords else options))
            self.opts_x_kws: list = deepcopy((self.opts_x_kws + self.final_opts if self.final_opts else self.opts_x_kws))
            self.use_in: bool = use_IN_req
            self.selection: bool = selection
            self.selection_d: dict = {0: self.opts_x_kws, 1: self.arguments}
            self.matches: list = []
            self.final_gate: bool = False

        def search_(self, text, cont):
            self.matches = [s for s in cont
                            if text in s]

        def start_(self, text, cont):
            self.matches = [s for s in cont
                            if s.startswith(text)]

        def complete(self, text, state):

            if state == 0:
                buffer = get_line_buffer()
                buffer_splt = get_line_buffer().split()
                if self.final_opts:
                    for fin in self.final_opts:
                        if fin in buffer: self.final_gate = True; break
                        else: self.final_gate = False
                if self.selection:
                    for k in self.selection_d:
                        if self.selection_d[k]:
                            for p in self.selection_d[k]:
                                if p in buffer: self.selection_d[k].remove(p)

                if self.use_in:

                    if text:

                        if self.final_gate:
                            self.search_(text, self.arguments)
                        elif self.arguments and len(buffer_splt) > 1 and buffer_splt[-2] in self.opts_wo_s:
                            self.search_(text, self.arguments)
                        else:
                            self.search_(text, self.opts_x_kws)

                    elif self.final_gate or (
                            self.arguments and len(buffer_splt) > 0 and buffer_splt[-1] in self.opts_wo_s
                    ):
                        self.matches = self.arguments[:]
                    else:
                        self.matches = self.opts_x_kws[:]

                elif text:

                    if self.final_gate:
                        self.start_(text, self.arguments)
                    elif self.arguments and len(buffer_splt) > 1 and buffer_splt[-2] in self.opts_wo_s:
                        self.start_(text, self.arguments)
                    else:
                        self.start_(text, self.opts_x_kws)

                elif self.final_gate or (
                        self.arguments and len(buffer_splt) > 0 and buffer_splt[-1] in self.opts_wo_s
                ):
                    self.matches = self.arguments[:]
                else:
                    self.matches = self.opts_x_kws[:]

            try:
                return self.matches[state]
            except IndexError:
                return None

    completer = Completer(opts, args)
    set_completer_delims(delims)
    set_completer(completer.complete)
    #parse_and_bind('^I: complete')


def pair_completer(stand_alone_opt_x_args1:list, stand_alone_opt_x_args2:list=None,
                   delims:str=' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?',
                   use_IN_req:bool=False, selection:bool=True):

    class Completer(object):

        def __init__(self):

            nonlocal stand_alone_opt_x_args1, stand_alone_opt_x_args2, use_IN_req, selection

            self.pairs: dict = {i: stand_alone_opt_x_args1[1] for i in stand_alone_opt_x_args1[0]}
            if stand_alone_opt_x_args2:
                for opt in stand_alone_opt_x_args2[0]: self.pairs[opt] = stand_alone_opt_x_args2[1]
            self.select: bool = selection
            self.use_in: bool = use_IN_req
            self.matches: list = []

        def search_(self, text, cont):
            self.matches = [s for s in cont
                            if text in s]

        def start_(self, text, cont):
            self.matches = [s for s in cont
                            if s.startswith(text)]

        def complete(self, text, state):
            if state == 0:
                buffer = get_line_buffer()
                b_opt = None
                gate = None
                pair_D = deepcopy(self.pairs)
                for opt in pair_D:
                    if opt in buffer: gate = True; b_opt = opt; break
                    else: gate = False
                if self.select and gate:
                    for i in self.pairs[b_opt]:
                        if i in buffer: pair_D[b_opt].remove(i)
                if self.use_in:
                    if gate:
                        if text: self.search_(text, pair_D[b_opt])
                        else: self.matches = pair_D[b_opt][:]
                    elif text: self.search_(text, pair_D)
                    else: self.matches = list(pair_D)[:]

                elif gate:
                    if text: self.start_(text, pair_D[b_opt])
                    else:
                        self.matches = pair_D[b_opt][:]
                elif text: self.start_(text, pair_D)
                else: self.matches = list(pair_D)[:]

            try:
                return self.matches[state]
            except IndexError:
                return None

    completer = Completer()
    set_completer_delims(delims)
    set_completer(completer.complete)
    #parse_and_bind('^I: complete')
