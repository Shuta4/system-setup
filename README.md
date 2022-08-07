# System setup
This script allows you to setup your system with config files located under `files` dir.

_Concept of this script and its final form and name are not defined, so it can be changed in the future. If you have some ideas please open an issue._

## Usage
1. Get `system-setup.py`.
2. `mkdir -p files/home files/root files/main` in the script's dir.
3. In `files/home` you can place files that will be copied to your `$HOME`.
4. In `files/root` you can place files that will be copied to your `/`.
5. In `files/main` you can place files that will:
	1. Overwrite files from `home` or `root` dirs (example: if you have files `files/home/test` and `files/main/test` the second one will be copied).
	2. Include content of `files/home` files with same paths where `#!include` is given (works only on text files).
	3. Be copied to your `$HOME` or `/` (depends on mode)
6. Run script like `python system-setup.py home` or `sudo python system-setup.py root` to copy files to your `$HOME` or `/` respectively.

## Different main for different users/machines
Currently i think that the best way will be to use git branches for it. Just start new branch with name `shared` (or something) from `master`, remove `.gitignore`, add dirs and files to `files/home` and `files/root`, then start new branch with name `username` or `machinename` (or something) from `shared` and add files to `files/main`. Then you will have the ability to manipulate all configs on all your machines/users in the one git repo.

## TODO
1. Search in `system-setup.py` for 'TODO'.
2. Rewrite script in OOP manner.
3. Put this script into the python package (so we need to separate it from files).
