import math
import os
import re
import shutil
import unicodedata
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple, Callable

import requests


def is_download_link(url):
    """ 
    Examples of download links:
    https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478986_1/xid-9478986_1 Tut1_CE2003
    https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478990_1/xid-9478990_1 Tut2_CE2003
    """
    pattern = r"bbcswebdav\/pid-\d+-dt-content-rid-\d+"
    return re.search(pattern, url) is not None


def get_content_id_from_listContent_url(url: str) -> Optional[str]:
    """get content id from list content url. The url contains the course id and the content id. Only
    return the content id

    Arguments:
        url {str} -- 

    Returns:
        Optional[str] -- content id
    """
    m = re.search(
        r"\/webapps\/blackboard\/content\/listContent\.jsp\?course_id=(_\d+_\d+)&content_id=(_\d+_\d+)",
        url,
    )
    if m is None:
        return None
    g = m.groups()
    return g[1]


def get_ids_from_listContent_url(url: str) -> Optional[Tuple[str, str]]:
    """return the course id and content id from the list content url in the form of a tuple

    Arguments:
        url {str} -- list content url

    Returns:
        Optional[Tuple[str, str]] -- tuple of course id and content id
    """
    m = re.search(
        r"\/webapps\/blackboard\/content\/listContent\.jsp\?course_id=(_\d+_\d+)&content_id=(_\d+_\d+)",
        url,
    )
    if m is None:
        return None
    g = m.groups()
    return (g[0], g[1])


def make_GET_request(BbRouter, path, params=None):
    cookies = {"BbRouter": BbRouter}
    headers = {
        "Connection": "keep-alive",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "X-Prototype-Version": "1.7",  # type: ignore
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "en-US,en;q=0.9",
    }

    return requests.get(path, headers=headers, cookies=cookies, params=params)


def get_predownload_link(url: str) -> str:
    # get predownload link for document
    if not url.startswith("https://ntulearn.ntu.edu.sg/bbcswebdav/") and url.startswith(
        "/bbcswebdav/"
    ):
        url = "https://ntulearn.ntu.edu.sg" + url
    if not is_download_link(url):
        raise ValueError("url: {} does not look like a download link".format(url))
    return url


def create_dummy_file(target_dir: str, name: str):
    """creates dummy file to signal that file of that name should be ignored. Dummy file has the 
    full path of: {target}/.{name}

    Args:
        target_dir (str): directory
        name (str): name of file
    
    Returns:
        (str): full path of dummp file
    """
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    full_path = get_dummy_file_path(target_dir, name)
    with open(full_path, "a"):  # Create file if does not exist
        pass
    return full_path


def get_dummy_file_path(target_dir: str, name: str):
    return os.path.join(target_dir, "." + name)


def dummy_file_exists(target_dir: str, name: str) -> bool:
    return os.path.exists(get_dummy_file_path(target_dir, name))


def sanitise_filename(value):
    """Sanitise filename by 
    1. replace slashes with hypens
    2. removing characters that aren't alphanumerics, underscores, or hyphens, or brackets.
    3. strip leading and trailing whitespace, dashes, and underscores.
    Args:
        value (string): safe filename
    """
    value = str(value)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[\\/]", "-", value)
    value = re.sub(r"[^\.()\w\s-]", "", value)
    value = value.strip("-_")
    return value


def download(
    BbRouter: str, url: str, destination: str, callback: Callable[[int, Optional[int]], None] = None
) -> bool:
    """download file, redirects will be involved. Even though download is invokes from a file object
    that has a name, the downloaded file name will be used instead

    Arguments:
        BbRouter {str} -- authentication token
        url {str} -- url
        destination {str} -- target file
        callback {int, Optional[int] -> None} -- callback hook to report progress, inputs to are
            bytes downloaded so far, and total file size, None if not available 

    Returns:
        bool -- [description]
    """
    cookies = {"BbRouter": BbRouter}
    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "en-SG,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    # if directory does not exist then create it
    dir_path = os.path.dirname(destination)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    if os.path.isfile(destination):
        return False

    with open(destination, "wb") as f:
        with requests.get(
            url, allow_redirects=True, stream=True, cookies=cookies, headers=headers
        ) as response:
            if callback:
                total_length_str = response.headers.get("content-length")
                total_length = int(total_length_str) if total_length_str is not None else None
                dl = 0
                with open(destination, "wb") as f:
                    for data in response.iter_content(chunk_size=1024):
                        dl += len(data)
                        f.write(data)
                        callback(dl, total_length)

            else:
                shutil.copyfileobj(response.raw, f)

    return True


def get_filename_from_url(url: str) -> Optional[str]:
    # find can return 0 index which is Python falsey
    if url.find("/") >= 0:
        filename = url.rsplit("/", 1)[1]
        return urllib.parse.unquote(filename)
    return None


def has_ext(url: str) -> bool:
    """returns whether download link contains file extension

    Arguments:
        url {str} -- download link

    Returns:
        bool -- True if contains file extension
    """
    filename = get_filename_from_url(url)
    if not filename:
        return False
    _name, ext = os.path.splitext(filename)
    return len(ext) > 0


def get_video_download_size(url: str) -> Optional[str]:
    res = requests.head(url, allow_redirects=True)

    size = res.headers["Content-Length"]
    if size:
        return convert_size(int(size))
    return None


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
