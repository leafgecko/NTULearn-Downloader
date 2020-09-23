"""
Storage: handles retrieving and updating data that is saved in the download directory. 

Currently the following data is stored:
- download_dir

Note that saved Folder object has the new attribute mapping of type Dict[str, int] that maps objects 
name to its index in Folder.children. This is to speed up merging
"""
import json
from pathlib import Path
import os
from typing import Dict, List

STORAGE_DIR = ".ntu_learn_downloader"
DOWNLOAD_DIR_FILENAME = "download_dir.json"


class Storage:
    def __init__(self, download_dir: str):
        """Load data if present, else initialize data

        Args:
            download_dir (str): download directory
        """
        self.dir = os.path.join(download_dir, STORAGE_DIR, "")
        Path(self.dir).mkdir(parents=True, exist_ok=True)

        download_dir_full_path = os.path.join(self.dir, DOWNLOAD_DIR_FILENAME)
        print(download_dir_full_path)
        if os.path.exists(download_dir_full_path):
            with open(download_dir_full_path, "r") as f:
                self.download_dir = json.load(f)
        else:
            self.download_dir = []

    def merge_download_dir(self, incoming_dir: List[Dict]):
        """mutate incoming_dir by merging it with saved download_dir, either adding download_links to file 
        and recorded_lecture objects if previously computed or initializing it with None. Assumed that 
        the topology of incoming dir is a superset of saved download_dir

        Args:
            incoming_dir (Dict): return value of api.get_download_dir
        """

        def traverse(saved_node: Dict, new_node: Dict):
            if saved_node is None:
                return
            node_type = new_node["type"]
            assert (
                saved_node["type"] == node_type
            ), "node type mismatch, LHS: {}, RHS: {}".format(
                saved_node["type"], node_type
            )

            if node_type in ["file", "recorded_lecture"]:
                new_node["download_link"] = saved_node.get("download_link")
                new_node["filename"] = saved_node.get("filename")
            elif node_type == "folder":
                mapping = saved_node["mapping"]
                saved_children = saved_node["children"]
                for new_child in new_node["children"]:
                    name = new_child["name"]
                    old_child = saved_children[mapping[name]] if name in mapping else None
                    traverse(old_child, new_child)

        # since download dir is of type list, need to recompute the top level mapping
        top_level_mapping: Dict[str, int] = {
            node["name"]: idx for idx, node in enumerate(self.download_dir)
        }
        for r_node in incoming_dir:
            l_node = (
                self.download_dir[top_level_mapping[r_node["name"]]]
                if r_node["name"] in top_level_mapping
                else None
            )
            traverse(l_node, r_node)

    def save_download_dir(self, download_dir: Dict):
        """first compute child name to index mappings and then save updated download_dir to storage

        Args:
            download_dir (Dict): update download_dir, files and recorded_lectures should have their
            filename and download link attributes present
        """

        def traverse(node):
            node_type = node["type"]
            if node_type == "folder":
                mapping = {
                    child["name"]: idx for idx, child in enumerate(node["children"])
                }
                node["mapping"] = mapping
                for child in node["children"]:
                    traverse(child)

        for node in download_dir:
            traverse(node)

        download_dir_full_path = os.path.join(self.dir, DOWNLOAD_DIR_FILENAME)
        self.download_dir = download_dir
        with open(download_dir_full_path, "w") as f:
            json.dump(download_dir, f)
