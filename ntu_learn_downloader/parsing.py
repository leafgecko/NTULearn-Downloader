from ntu_learn_downloader.smodels import SDoc, SFolder, SLecture
from bs4 import BeautifulSoup
import re
from typing import List, Union
from ntu_learn_downloader.utils import is_download_link
from ntu_learn_downloader.constants import GET_CONTENT_LIST_URL

def parse_recorded_lecture_contents(html: str) -> str:
    m1 = re.search(r'var gsUserId\s+= "(\S+)";', html)
    m2 = re.search(r'var gsModuleId\s+= "(\S+)";', html)
    m3 = re.search(r'addStreamInfo\("NTU-ME\d+", "(.*)", "", "", "", "as"\)', html)

    if m1 is None or m2 is None or m3 is None:
        raise ValueError('Unable to get mp4 download link')
    gsUserId, gsModuleId = m1.groups()[0], m2.groups()[0]
    domain = m3.groups()[0]
    url = "https://" + domain + "/content/" + gsUserId + "/" + gsModuleId + "/media/1.mp4"

    return url

def parse_content_page(soup) -> List[Union[SDoc, SFolder, SLecture]]:
    # NOTE e.g. "course_id": "_306327_1", "content_id": "_1790226_1"
    contentList = soup.find("ul", {"id": "content_listContainer"})
    if contentList is None:
        return []
    children = [c for c in contentList.children if c.name is not None]

    result: List[Union[SDoc, SFolder, SLecture]] = []

    def is_content_folder(child, img):
        return img is not None and img.get("alt") == "Content Folder"

    def is_item(child, img):
        # some items do not have the item icon
        return img is not None and (
            img.get("alt") == "Item"
            or (img.get("alt") == "" and child.find("div", {"class": "item clearfix"}))
        )

    def is_AcuStudio(child, img):
        return img is not None and img.get("alt") == "AcuStudio"

    def is_file(child, img):
        return img is not None and img.get("alt") == "File"
    
    for c in children:
        img = c.find("img")
        if is_content_folder(c, img):
            hyperlink = c.find("a")
            name = hyperlink.text
            link = hyperlink.get("href")
            details = c.find("div", {"class": "details"}).text
            result.append(SFolder(name.strip(), link.strip(), details.strip(), None))
        elif is_item(c, img):
            folder = __item_to_folder(c)
            if folder:
                result.append(folder)
        elif is_AcuStudio(c, img):
            # ignore that for now
            hyperlink = c.find("a")
            name = hyperlink.text
            link = hyperlink.get("href")
            result.append(SLecture(name.strip(), link))
        elif is_file(c, img):
            hyperlink = c.find("a")
            name = hyperlink.text
            link = hyperlink.get("href")
            result.append(SDoc(name.strip(), link))
        else:
            pass

    return result


def __item_to_folder(item):
    folder_name = item.find("h3").text
    details = item.find("div", {"class", "details"})

    dl_links = [a for a in details.find_all("a") if is_download_link(a.get("href"))]
    children = []
    for a_tag in dl_links:
        link, name = a_tag.get("href"), a_tag.text
        children.append(SDoc(name=name.strip(), link=link))
    if children:
        return SFolder(name=folder_name.strip(), link=None, details="", children=children)
    return None
