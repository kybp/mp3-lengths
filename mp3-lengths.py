import argparse
import os
import sys

from mutagen.mp3 import HeaderNotFoundError, MP3

def print_error(message):
    print('{}: {}'.format(sys.argv[0], message), file=sys.stderr)

def length_in_seconds(filename):
    try:
        return int(MP3(filename).info.length)
    except HeaderNotFoundError:
        return None

def file_lengths(files, toplevel=True):
    lengths = dict()

    for filename in files:
        if os.path.isdir(filename) and toplevel:
            def join_path(path):
                return os.path.join(filename, path)
            dir_files = map(join_path, os.listdir(filename))
            lengths[filename] = file_lengths(dir_files, False)
        elif os.path.isdir(filename):
            print_error('{}: is a directory'.format(filename))
        elif os.path.isfile(filename):
            lengths[filename] = length_in_seconds(filename)
        else:
            print_error('{}: no such file'.format(filename))

    return lengths

def file_lengths_recursive(files):
    lengths = dict()

    for path in files:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    lengths[full_path] = length_in_seconds(full_path)
        elif os.path.isfile(path):
            lengths[path] = length_in_seconds(path)
        else:
            print_error('{}: no such file'.format(path))

    return lengths

def print_summary(lengths):
    for song, length in sorted(lengths.items()):
        if length is None:
            print_error('{}: not an MP3'.format(song))
        elif isinstance(length, dict):
            print_summary(length)
        else:
            print_length(song, length)

def print_length(song, length):
    hours   = length // 3600
    minutes = (length % 3600) // 60
    seconds = length % 60
    if hours > 0:
        minutes 
        print('%02d:%02d:%02d\t%s' % (hours, minutes, seconds, song))
    else:
        print('%02d:%02d\t%s' % (minutes, seconds, song))

def print_total(lengths):
    def sum_dict(lengths):
        total_seconds = 0
        for song, length in sorted(lengths.items()):
            if length is None:
                pass
            elif isinstance(length, dict):
                total_seconds += sum_dict(length)
            else:
                total_seconds += length
        return total_seconds
    print_length('Total', sum_dict(lengths))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print lengths of MP3 files')
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='an MP3 or a directory to search')
    parser.add_argument('-r', '--recursive',
                        dest='recursive', action='store_true',
                        help='recursively search subdirectories')
    parser.add_argument('-t', '--total',
                        dest='get_total', action='store_true',
                        help='only print the total length for all files')
    parser.set_defaults(recursive=False, get_total=False)
    args = parser.parse_args()

    if args.recursive:
        lengths = file_lengths_recursive(args.files)
    else:
        lengths = file_lengths(args.files)

    if args.get_total:
        print_total(lengths)
    else:
        print_summary(lengths)
