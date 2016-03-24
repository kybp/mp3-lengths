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

def print_summary(lengths, print_readable):
    for song, length in sorted(lengths.items()):
        if length is None:
            print_error('{}: not an MP3'.format(song))
        elif isinstance(length, dict):
            print_summary(length, print_readable)
        else:
            print_length(song, length, print_readable)

def print_length(song, length, print_readable):
    hours   = length // 3600
    minutes = (length % 3600) // 60
    seconds = length % 60
    if print_readable:
        days = hours // 24
        hours %= 24
        weeks = days // 7
        days %= 7
        print('{}: '.format(song), end='')
        if weeks   > 0: print('{} weeks, '  .format(weeks),   end='')
        if days    > 0: print('{} days, '   .format(days),    end='')
        if hours   > 0: print('{} hours, '  .format(hours),   end='')
        if minutes > 0: print('{} minutes, '.format(minutes), end='')
        print('{} seconds'.format(seconds))
    else:
        if hours > 0:
            minutes 
            print('%02d:%02d:%02d\t%s' % (hours, minutes, seconds, song))
        else:
            print('%02d:%02d\t%s' % (minutes, seconds, song))

def print_total(lengths, print_readable):
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
    print_length('Total', sum_dict(lengths), print_readable)

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
    parser.add_argument('-H', '--readable',
                        dest='readable', action='store_true',
                        help='print times in human readable format')
    parser.set_defaults(recursive=False, get_total=False)
    args = parser.parse_args()

    if args.recursive:
        lengths = file_lengths_recursive(args.files)
    else:
        lengths = file_lengths(args.files)

    if args.get_total:
        print_total(lengths, args.readable)
    else:
        print_summary(lengths, args.readable)
