from argparse import ArgumentParser
from pathlib import Path
from shutil import copy2, move
from tempfile import TemporaryDirectory


def get_args():
    parser = ArgumentParser(description="Setup your system with config files")
    parser.add_argument('mode', choices=['home', 'root'])
    return parser.parse_args()


def is_binary(path: Path) -> bool:
    # Checks if give Path object is binary file.
    # Thanks to https://stackoverflow.com/a/7392391 for this solution.
    if not path.is_file():
        return False

    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    with open(path, 'rb') as f:
        b = f.read(1024)
        return bool(b.translate(None, textchars))


def process_files(in_dir: Path, out_dir: Path, shared_dir: Path = None):
    for p in in_dir.iterdir():
        dest = out_dir / p.name
        shared_p = None
        if shared_dir is not None:
            shared_p = shared_dir / p.name
        if not dest.is_dir() and dest.exists():
            # For now we will not do anything on existing in system files
            # to prevent their content replacement.
            # TODO: calculate checksum on existing file and compare it with
            #       the one that were got from this file when it was copied
            #       by this script before (need to store checksums somewhere).
            #       If checksums are same then just do all the stuff,
            #       else request merge from user.
            continue

        if p.is_symlink():
            # We will just copy the symlink to out_dir/<filename>
            # preserving as much attributes as possible.
            copy2(p, dest, follow_symlinks=False)

        elif p.is_dir():
            # If directory already exists just recursively go through it,
            # else create dir in out_dir preserving attrs.
            # TODO: maybe, we need to change attributes of an existing dir.
            if not dest.exists():
                dest.mkdir(mode=p.lstat().st_mode)
            process_files(p, dest, shared_p)

        elif p.is_file():
            # For binary files we just copies them to dest.
            # For text files if file in shared_dir exists we will
            # first copy p into temp file and then update its content
            # with those from file in shared_dir, then we will move
            # temp file to dest preserving file's attrs.
            if not is_binary(p) and shared_p is not None and shared_p.exists():
                with TemporaryDirectory() as temp_dir_path:
                    temp_dir = Path(temp_dir_path)
                    tmp = temp_dir / p.name
                    with p.open('r') as pf:
                        with tmp.open('w') as tf:
                            for line in pf:
                                # TODO: accept other comment syntaxes like '//!include'.
                                # TODO: make it possible to include part of file or
                                #       custom file like '#!include <10,20>' includes
                                #       only shared file's lines from 10 to 20 and
                                #       '#!include custom.sh' includes 'files/custom/custom.sh'.
                                #       Of course we should give possibility to combine this
                                #       variants like '#!include custom.sh <10,20>'.
                                if line.lower().startswith('#!include'):
                                    with shared_p.open('r') as sf:
                                        for sline in sf:
                                            tf.write(sline)

                                else:
                                    tf.write(line)
                    move(tmp, dest)
                    dest.lchmod(p.lstat().st_mode)
            else:
                copy2(p, dest)


    if shared_dir is not None and shared_dir.exists():
        # This copies files that are not presented in in_dir but
        # are presented in shared_dir, excluding files content processing.
        process_files(shared_dir, out_dir)


def main():
    args = get_args()
    script_dir = Path(__file__).resolve().parent
    files_dir = script_dir / 'files'

    if args.mode == 'home':
        out_dir = Path.home()
    else:
        out_dir = Path('/')

    in_dir = files_dir / 'main'
    shared_dir = files_dir / args.mode
    process_files(in_dir, out_dir, shared_dir)


if __name__ == "__main__":
    main()
