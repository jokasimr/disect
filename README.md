# disect

Disect is a command line tool for finding the dependencies that caused a regression in a python environment.


## Install

```
curl https://raw.githubusercontent.com/jokasimr/disect/refs/heads/main/disect.py > $HOME/.local/bin/disect
chmod u+x $HOME/.local/bin/disect
```

## Usage

```
$ disect --help

disect is a program that helps you find what dependencies caused a regression.
It minimizes the number of environments that needs to be tested by leveraging combinatorical group testing.
It works similar to 'git bisect', and will repeatedly ask the user to mark
dependency sets as good or bad, splitting the search space based on the results.

To run it you need to provide:
    1. A pip requirements file where the dependencies that might have caused the regression
       are pinned to known good versions.
    2. A filename where the prgram will write the next environment to be tested.

usage: disect GOOD_DEPS NEW_DEPS <command>

Commands:
  start        Begin a dependency bisect session
  good         Mark the last test result as good
  bad          Mark the last test result as bad
```
