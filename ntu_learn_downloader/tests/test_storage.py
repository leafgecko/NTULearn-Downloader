import unittest
import shutil
import os
import json
from pathlib import Path

from typing import Dict, List
from ntu_learn_downloader import Storage

temp_dir = "test/temp/"  # TODO this path should be absolute
storage_dir = os.path.join(temp_dir, ".ntu_learn_downloader", "")
FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "download_dir_fixtures")


def remove_test_files():
    if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
        # print("removing test generated files")
        shutil.rmtree(temp_dir)


class BaseTestStorage(unittest.TestCase):
    def assertObjEquals(self, rhs, lhs, is_saved=False):
        """utility method to recursively compare serialized folders. 

        Args:
            rhs (Union[List, Dict]): Folder/File/Recorded Lecture
            lhs (Union[List, Dict]): Folder/File/Recorded Lecture
            is_saved (bool): set if checking download_dir saved to Storage, checks mapping as well
        """

        if isinstance(lhs, list) and isinstance(rhs, list):
            self.assertEqual(len(lhs), len(rhs))
            for l_folder in lhs:
                r_folder = next(n for n in rhs if n["name"] == l_folder["name"])
                self.assertObjEquals(l_folder, r_folder)
            return

        self.assertEqual(rhs["type"], lhs["type"])
        self.assertEqual(rhs["name"], lhs["name"])
        if lhs["type"] == "folder":
            if is_saved:
                self.assertDictEqual(rhs['mapping'], lhs['mapping'])
            self.assertEqual(len(lhs["children"]), len(rhs["children"]))
            for child in lhs["children"]:
                r_child = next(c for c in rhs["children"] if c["name"] == child["name"])
                self.assertObjEquals(child, r_child, is_saved)
        else:
            if "filename" in rhs or "filename" in lhs:
                try:
                    self.assertEqual(rhs["download_link"], lhs["download_link"])
                    self.assertEqual(rhs["filename"], lhs["filename"])
                except Exception:
                    import pdb; pdb.set_trace() # DEBUG
            self.assertEqual(rhs["predownload_link"], lhs["predownload_link"])


class TestNewStorage(BaseTestStorage):
    @classmethod
    def setup_class(cls):
        remove_test_files()

    @classmethod
    def tearDownClass(cls):
        remove_test_files()

    def test_initialize_new_download_dir(self):
        storage = Storage(temp_dir)
        self.assertEqual([], storage.download_dir)
        # check that hidden directory has been created
        self.assertTrue(os.path.exists(storage_dir))

        with open(os.path.join(FIXTURES_PATH, "CE3007_download_subset.json")) as f:
            loaded_download_dir = json.load(f)
        loaded_download_dir_copy = loaded_download_dir.copy()

        storage.merge_download_dir(loaded_download_dir)
        self.assertObjEquals(loaded_download_dir, loaded_download_dir_copy)

        storage.save_download_dir(loaded_download_dir)
        with open(
            os.path.join(FIXTURES_PATH, "CE3007_expected_download_subset.json")
        ) as f:
            expected = json.load(f)
        self.assertObjEquals(expected, storage.download_dir, is_saved=True)

        # check that data has been saved to disk
        next_storage = Storage(temp_dir)
        result = next_storage.download_dir
        self.assertObjEquals(expected, result, is_saved=True)


class TestExistingStorage(BaseTestStorage):
    @classmethod
    def setup_class(cls):
        remove_test_files()
        Path(storage_dir).mkdir(parents=True, exist_ok=True)

        shutil.copyfile(
            os.path.join(FIXTURES_PATH, "CE3007_expected_download_subset.json"),
            os.path.join(storage_dir, "download_dir.json"),
        )

    @classmethod
    def tearDownClass(cls):
        remove_test_files()

    def test_existing_download_dir(self):
        storage = Storage(temp_dir)
        # quick check to see if storage directory was initialized correctly
        with open(
            os.path.join(FIXTURES_PATH, "CE3007_expected_download_subset.json")
        ) as f:
            expected_init = json.load(f)
            self.assertObjEquals(expected_init, storage.download_dir)

        # incoming new download subset 2
        with open(
            os.path.join(FIXTURES_PATH, 'CE3007_predownload_subset_2.json')
        ) as f:
            incoming_download_dir = json.load(f)
        storage.merge_download_dir(incoming_download_dir)
        with open(
            os.path.join(FIXTURES_PATH, 'CE3007_expected_merged_predownload_subset_2.json')
        ) as f:
            expected = json.load(f)
        self.assertObjEquals(expected, incoming_download_dir)

        storage.save_download_dir(incoming_download_dir)

        # check that data has been saved to disk
        next_storage = Storage(temp_dir)
        result = next_storage.download_dir
        self.assertObjEquals(expected, result, is_saved=True)

            
        



