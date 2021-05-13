from os import makedirs, environ
from threading import Thread
from subprocess import Popen
from sys import stdout


class MakeDir(Thread):

    def __init__(self, array:list=None):
        Thread.__init__(self)
        self.array = array

    def run(self) -> None:
        for p in self.array:
            p = (f"{environ['HOME']}{p[1:]}" if p.startswith('~/') else p)
            makedirs(p, mode=0o770, exist_ok=True)


def get_all_until_iteration(g):
    try:
        content = next(g)
    except StopIteration:
        return None
    return content


def watch_on_q(q):
    while True:
        x = q.get()
        if x:
            p = Popen([x], shell=True)
            try:
                p.communicate()
            except Exception as e:
                print(f" [[WARN] {e}]", file=stdout)
        else: break
