from typing import List, Union, Dict

from ntu_learn_downloader import api
from ntu_learn_downloader.parsing import parse_content_page
from ntu_learn_downloader.utils import (
    get_ids_from_listContent_url,
    get_predownload_link,
)


class Base:
    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ",\n\t".join(
                ["{}= {}".format(k, v.__repr__()) for k, v in self.__dict__.items()]
            )
            + ")"
        )

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and all(
            other.__dict__[k] == v for k, v in self.__dict__.items()
        )

    def serialize(self, BbRouter: str) -> Dict:
        return {}


class Folder(Base):
    def __init__(self, name, link, details, children=None):
        self.name = name
        self.link = link
        self.details = details
        self.children = children

    def load_children(self, BbRouter: str):
        if not self.children is None:
            return
        course_content_id = (
            get_ids_from_listContent_url(self.link) if self.link else None
        )
        children: List[MODEL_TYPES] = []
        if course_content_id is not None:
            course_id, content_id = course_content_id
            soup = api.make_get_contents_request(BbRouter, course_id, content_id)
            children = [to_model(c) for c in parse_content_page(soup)]
        self.children = children

    def serialize(self, BbRouter: str) -> Dict:
        # convert Folder into a Python dictionary, note that it recursively serializes its children
        if self.children is None:
            self.load_children(BbRouter)
        return {
            "type": "folder",
            "name": self.name,
            "children": [x.serialize(BbRouter) for x in self.children]
            if self.children
            else [],
        }

    def __eq__(self, other):
        # compare atttribute and recursively check the children
        return Base.__eq__(self, other) and (
            (self.children is None and other.children is None)
            or all(c1 == c2 for c1, c2 in zip(self.children, other.children))
        )


class Doc(Base):
    def __init__(self, name, link):
        # links come in as a relative path, so when serializing, need to convert to full path to
        # predownload link (need redirect to get final download link)
        self.name = name
        self.link = link

    def serialize(self, BbRouter: str, load_download_links: bool = False) -> Dict:
        predownload_link = get_predownload_link(self.link)
        return {"type": "file", "name": self.name, "predownload_link": predownload_link}


class RecordedLecture(Base):
    def __init__(self, name, predownload_link):
        self.name = name
        self.predownload_link = predownload_link

    def serialize(self, BbRouter: str) -> Dict:
        return {
            "type": "recorded_lecture",
            "name": self.name,
            "predownload_link": self.predownload_link,
        }


MODEL_TYPES = Union[Folder, Doc, RecordedLecture]


def to_model(smodel) -> MODEL_TYPES:
    classname = smodel.__class__.__name__
    if classname == "SFolder":
        return Folder(
            name=smodel.name,
            link=smodel.link,
            details=smodel.details,
            children=[to_model(c) for c in smodel.children]
            if smodel.children
            else None,
        )
    elif classname == "SDoc":
        return Doc(name=smodel.name, link=smodel.link)
    elif classname == "SLecture":
        return RecordedLecture(name=smodel.name, predownload_link=smodel.link)
    raise Exception("unexpcted type")
