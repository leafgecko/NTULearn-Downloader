import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List

from ntu_learn_downloader import (
    authenticate,
    get_courses,
    get_download_dir,
    get_file_download_link,
    get_recorded_lecture_download_link,
)
from ntu_learn_downloader.utils import (
    download,
    get_filename_from_url,
    get_video_download_size,
    sanitise_filename,
    create_dummy_file,
    dummy_file_exists
)

parser = argparse.ArgumentParser(description="CLI wrapper to NTULearn Downloader")

# Authentication
parser.add_argument(
    "-username",
    type=str,
    help="username including domain name (e.g. username@student.main.ntu.edu.sg)",
)
parser.add_argument("-password", type=str, help="password")

# Other flags
parser.add_argument(
    "--download_to",
    type=str,
    help="Download destination (required if downloading files)",
)
parser.add_argument(
    "--ignore",
    type=str,
    help="Comma seperated list of modules to ignore, will ignore module if it contains any of the supplied values (e.g. CE2006)",
)
parser.add_argument(
    "--ignore_files",
    action="store_true",
    help="Ignore downloading of files, useful if only downloading lectures",
)
parser.add_argument(
    "--download_recorded_lectures",
    action="store_true",
    help="Download recorded lectures. WARNING downloading large files",
)
parser.add_argument(
    "--sem",
    type=str,
    help="Which semester to download from (e.g. AY2019/20 Semester 2 would be 19S2, see you are taking the following courses output)",
)
parser.add_argument(
    "--prompt",
    action="store_true",
    help="Prompt whether to download lecture video or files above set (set with --max_size)",
)


def download_files(
    BbRouter: str,
    obj: Dict,
    download_path: str,
    ignore_files: bool = False,
    ignore_recorded_lectures: bool = False,
    to_prompt: bool = False,
):
    if obj["type"] == "folder":
        download_path = os.path.join(download_path, sanitise_filename(obj["name"]), "")
        for c in obj["children"]:
            download_files(
                BbRouter,
                c,
                download_path,
                ignore_files,
                ignore_recorded_lectures,
                to_prompt,
            )
    elif obj["type"] == "file":
        if ignore_files:
            return
        download_link = get_file_download_link(BbRouter, obj["predownload_link"])
        filename = get_filename_from_url(download_link)
        if filename is None:
            print("Unable to get filename from: {}".format(download_link))
            return
        full_file_path = os.path.join(download_path, sanitise_filename(filename))
        # although we get the filename from the download link, some have the same name as in the
        # download link so we can potentially save a network call here
        if os.path.exists(full_file_path) :
            return
        print("- {}".format(full_file_path))
        download(BbRouter, download_link, full_file_path)
        return
    elif obj["type"] == "recorded_lecture":
        if ignore_recorded_lectures:
            return
        # can infer video name without expensive call to get download link
        video_name = sanitise_filename(obj["name"] + ".mp4")
        full_file_path = os.path.join(download_path, video_name)
        if os.path.exists(full_file_path) or dummy_file_exists(download_path, video_name):
            return
        download_link = get_recorded_lecture_download_link(
            BbRouter, obj["predownload_link"]
        )
        video_size = get_video_download_size(download_link)
        to_download = True
        if to_prompt:
            to_download = (
                query_yes_no(
                    "Download {}, ({})? ['Enter' for Y]".format(video_name, video_size), default="yes"
                )
                == "yes"
            )
        if to_download:
            print("- {} ({})".format(full_file_path, video_size or "Unknown"))
            download(BbRouter, download_link, full_file_path)
        else:
            dummy_file_path = create_dummy_file(download_path, video_name)
            print("Created dummy file:", dummy_file_path)

        return


def in_ignored_modules(module, ignored_list):
    return any(x in module for x in ignored_list)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": "yes", "y": "yes", "ye": "yes", "no": "no", "n": "no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


if __name__ == "__main__":
    args = parser.parse_args()
    bbrouter = authenticate(args.username, args.password)

    print("you are taking the following courses:")
    courses = get_courses(bbrouter)
    for course_name, course_id in courses:
        print("- {}".format(course_name))

    if args.download_to:
        print("\n\nDownloading to {}".format(args.download_to))

        ignore_recorded_lectures = False if args.download_recorded_lectures else True
        ignored_modules: List[str] = []
        if args.ignore:
            ignored_modules = args.ignore.split(",")
            ignored_modules = [s.upper() for s in ignored_modules]

        for name, course_id in courses:
            if args.sem and not name.startswith(args.sem):
                continue
            if in_ignored_modules(name, ignored_modules):
                continue
            print(name)
            course_folder = get_download_dir(bbrouter, name, course_id)

            download_files(
                bbrouter,
                course_folder,
                args.download_to,
                ignore_files=args.ignore_files,
                ignore_recorded_lectures=not args.download_recorded_lectures,
                to_prompt=args.prompt,
            )

    print("DONE")
