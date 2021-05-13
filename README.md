# botnc
This framework is writen for a correlation between regular expressions and filesystem-managing. 

The basic idea; to indicate any file (including the associated path) in a System, to manipulate them in addition, and
summarize in a valid command-string. For a simple description: mass-renamer written in python. In fact; the result is 
a dynamic module to select, bulk and manipulate file-paths; to use it in own syntax for command-line-program's of the 
operating system. 

****
**Setup**

Script: 'botnc.py', line 3.

([extent $PATH and $PYTHONPATH])

****
**Usage**

There are three methods to execute the script:

1. in Terminal with(out) args to run the cli without auto-completion
2. in python-shell for auto-completion-support
3. as one-line-command.

@1: root; regular-expression-rules for collecting and selecting; to follow-links, 
needs to be specified by script-args (by derogation of default).

@2: regular-expression-rules for collecting and selecting, needs to be specified by 
overwriting the variables in 'botnc_main/default_kw_args'.

_each cli-instance has its own help-page_
****
**How it bulks**

In cli-instances "collect" and "preserve", it is possible to set a KEY direct after the sharp, who will represents the 
collected content for later use.
Requested otherwise. This KEY will formated and additional forked.

If the Selected will not preserved, so the key will forked to:
`§KEY`: representing a list of maps; `§KEY.<num>`: represents one map;
 `§KEY.<num>.p`: represents the `<num>`-path; `§KEY.<num>.f`: represents the `<num>`-files.

If the Selected will preserved, so the basic `§KEY` hold the basic-content and the preserved augmentation, to perform the
command-form like: '/basic/path/to/files.txt /preserved/path/to/files.preserved'. For separate use, the
key-palette is extended by `§KEY.<num>.a`, `§KEY.<num>.a.p` and `§KEY.<num>.a.f`.

Usage-methode 3 supports theoretically the same structure, but because the evaluation of the numbers can be difficult;
this methode supports the `.n` to represent all `<nums>`.
****
**How it performs**

For example: a backup from any zipped logfile in /var/log is recommended, also to hide the backup-files and to check the
backup-process with a dated logfile. 

./botnc.py -t /var/log/ -m "{'map_kwargs': {0: 'log$'}, 'collect_kwargs': {1: '\.gz$'}, 
'preserve_kwargs': {1: ['^|^\.', '.']}}" -c 'cp -v §§§.n §§ BACKUP\DIR §§ §§§.n.a.f >> § ~/file.log at- § \S $(date)'

_see botnc-manual-page for more about the botnc-syntax_

**Notes**
1. No spaces are appended to path-specifications
2. each file stored in a key, startswith slash '/'
3. ... every path stored in a key, doesn't endswith slash '/'
4. '~' will not escaped
****
_This script is writen on and for Linux. Not tested on Windows_

****

![botnc_ex1](https://user-images.githubusercontent.com/84026287/118095854-e1ee6a80-b3d0-11eb-8c04-b8067b217d04.png)
![botnc_ex2](https://user-images.githubusercontent.com/84026287/118095865-e6b31e80-b3d0-11eb-914f-a8a515df6800.png)

