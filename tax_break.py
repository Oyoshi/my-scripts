import git
import zipfile
import os
import argparse
import datetime
from pathlib import Path


class DateRange:
    def __init__(self, begin_date, end_date):
        self.begin_date = begin_date
        self.end_date = end_date


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--author',
        metavar='<arg>',
        required=True,
        nargs='+',
        help='author of changes')
    parser.add_argument(
        '-b',
        '--branch',
        metavar='<arg>',
        required=True,
        help='branch name')
    return parser.parse_args()


def generate_default_date_range():
    begin_date = generate_default_begin_date()
    end_date = generate_default_end_date()
    return DateRange(begin_date, end_date)


def generate_default_begin_date():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, 1)


def generate_default_end_date():
    return datetime.datetime.today()


def filter_commits(args, date_range):
    repo_path = os.getcwd()
    git_repo = git.Git(repo_path)
    files_log_info = git_repo.log(
        args.branch,
        f'--author={create_author(args.author)}',
        f'--since={date_range.begin_date}',
        f'--until={date_range.end_date}',
        '--pretty=tformat:',
        '--name-only')
    unique_files = get_unique_files_from_commits(files_log_info)

    hashes_log_info = git_repo.log(
        args.branch,
        f'--author={create_author(args.author)}',
        f'--since={date_range.begin_date}',
        f'--until={date_range.end_date}',
        '--format=%H')
    hashes = split_hashes(hashes_log_info)
    diffs = {}
    for hash_commit in hashes:
        diffs[hash_commit] = git_repo.show(hash_commit)
    return unique_files, diffs


def create_author(splitted_author):
    return ' '.join(splitted_author)


def get_unique_files_from_commits(log_info):
    return set(log_info.split('\n'))


def split_hashes(log_info):
    return log_info.split('\n')


def create_archive(files, diffs):
    top_level_dirname = create_toplevel_dirname()
    Path(top_level_dirname).mkdir(parents=True, exist_ok=True)
    create_archive_with_files(top_level_dirname, files)
    create_archive_with_diffs(top_level_dirname, diffs)


def create_toplevel_dirname():
    return f"my_changes_{str(datetime.datetime.today().date()).replace('-', '_')}"


def create_archive_with_files(top_level_dirname, files):
    changed_files_dirname = os.path.join(top_level_dirname, 'files.zip')
    zipf = zipfile.ZipFile(changed_files_dirname, 'w')
    for file in files:
        zipf.write(
            file,
            os.path.basename(file),
            compress_type=zipfile.ZIP_DEFLATED)
    zipf.close()


def create_archive_with_diffs(top_level_dirname, diffs):
    diffs_dirname = os.path.join(top_level_dirname, 'diffs.zip')
    zipf = zipfile.ZipFile(diffs_dirname, 'w')
    for hash_commit, diff in diffs.items():
        file = f'{hash_commit}.diff'
        zipf.writestr(file, diff)
    zipf.close()


def main():
    args = parse_args()
    date_range = generate_default_date_range()
    files, diffs = filter_commits(args, date_range)
    create_archive(files, diffs)


if __name__ == '__main__':
    main()
