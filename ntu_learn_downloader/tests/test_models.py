import unittest
from unittest.mock import patch

from ntu_learn_downloader.tests.mock_server import MOCK_CONSTANTS
from ntu_learn_downloader import get_courses, get_content_ids

from ntu_learn_downloader.api import parse_content_page
from ntu_learn_downloader.models import Folder, Doc, RecordedLecture

BbRouter = "expires:1583963361,id:1A633268311FA435A6HT7K968346A658,signature:bqguvcoi0nh434robmpzervdtpomolh17rk3m9kxhiy0ozd5tzquhd0e4igldygm,site:5ecaf6aa-60ca-4431-89e7-6ed4c720440d,timeout:10800,user:6itk73437hq6tbcznl60t354qc2vn2py,v:2,xsrf:y3d3nzrg-c301-4455-a5a3-hpjdect1jyil"


class TestModels(unittest.TestCase):
    def test_folder_get_children(self):

        folder = Folder(
            name="Tutorial solutions",
            link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875200_1",
            details="\n\nThis folder contains the tutorial solutions\n\n   \n",
            children=None,
        )

        expected = [
            Doc(
                name="Tut1_CE2003_soln",
                link="/bbcswebdav/pid-1875202-dt-content-rid-9478989_1/xid-9478989_1",
            ),
            Doc(
                name="Tut2_CE2003_soln",
                link="/bbcswebdav/pid-1875203-dt-content-rid-9478994_1/xid-9478994_1",
            ),
            Doc(
                name="Tut3_CE2003_soln",
                link="/bbcswebdav/pid-1875204-dt-content-rid-9478999_1/xid-9478999_1",
            ),
            Doc(
                name="Tut4_CE2003_soln",
                link="/bbcswebdav/pid-1875205-dt-content-rid-9479003_1/xid-9479003_1",
            ),
            Doc(
                name="Tut5_CE2003_soln",
                link="/bbcswebdav/pid-1875206-dt-content-rid-9479007_1/xid-9479007_1",
            ),
            Doc(
                name="Tut7_CE2003_soln",
                link="/bbcswebdav/pid-1875207-dt-content-rid-9479012_1/xid-9479012_1",
            ),
            Doc(
                name="Tut8_CE2003_soln",
                link="/bbcswebdav/pid-1875208-dt-content-rid-10950997_1/xid-10950997_1",
            ),
            Doc(
                name="Tut9_CE2003_soln",
                link="/bbcswebdav/pid-1875209-dt-content-rid-9479024_1/xid-9479024_1",
            ),
            Doc(
                name="Tut10_CE2003_soln",
                link="/bbcswebdav/pid-1875210-dt-content-rid-9478985_1/xid-9478985_1",
            ),
            Doc(
                name="tut10_alt_answerQ2",
                link="/bbcswebdav/pid-1875211-dt-content-rid-9478981_1/xid-9478981_1",
            ),
            Folder(
                name="Soln to Mod 1 exercise",
                link=None,
                details="",
                children=[
                    Doc(
                        name="Mod1_Homework_soln",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1980456-dt-content-rid-10080708_1/xid-10080708_1",
                    )
                ],
            ),
        ]

        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            folder.load_children(BbRouter)
            self.assertListEqual(expected, folder.children)

    def test_folder_serialize(self):
        folder = Folder(
            name="Tutorials",
            link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875198_1",
            details="Tutorials for the whole course. Solutions are uploaded towards the end of semester. Tutorials commence in Week 2.",
            children=None,
        )
        expected = {
            "type": "folder",
            "name": "Tutorials",
            "children": [
                {
                    "type": "folder",
                    "name": "tut4_video",
                    "children": [
                        {
                            "type": "recorded_lecture",
                            "name": "tut4_intro",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=20021241ee3767af20bc10a41a131843c3eab5&parent_id=_1790226_1&course_id=_306327_1&am_course_id=192946&ver=7&content_id=_1997338_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "tut4_part1",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=2002122430141911382bce70db2d1723b9c583&parent_id=_1790226_1&course_id=_306327_1&am_course_id=192955&ver=7&content_id=_1997531_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "tut4_part2",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=200212554fdfd70f65fc735141955ffb349ee1&parent_id=_1790226_1&course_id=_306327_1&am_course_id=192956&ver=7&content_id=_1997530_1",
                        },
                    ],
                },
                {
                    "type": "folder",
                    "name": "Tut5_video",
                    "children": [
                        {
                            "type": "recorded_lecture",
                            "name": "Tut5_intro",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=2002149f9f1a3133251425d4ffaa1873d2a10e&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193270&ver=7&content_id=_2002376_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut5_Q1",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=2002147632d13340277f913b1cab5f56ae3235&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193271&ver=7&content_id=_2002431_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut5_Q2",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=20021424e133513d426c3342a68358b11da194&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193272&ver=7&content_id=_2002433_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut5_Q3",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=200214eea4fdf6ccfde8012fe8f3e713363992&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193273&ver=7&content_id=_2002437_1",
                        },
                    ],
                },
                {
                    "type": "folder",
                    "name": "Tut7_video",
                    "children": [
                        {
                            "type": "recorded_lecture",
                            "name": "Tut7_intro",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=20021727e7dae49a81657457999744194acbc0&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193464&ver=7&content_id=_2005197_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut7_Q1",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=200217d7afa455d8999df2f3aacff251659331&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193476&ver=7&content_id=_2005211_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut7_Q2&3",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=200217170037712c4240abcc3f370ecde641a7&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193483&ver=7&content_id=_2005209_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut7_Q4",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=2002179bae8f80c2f50d6170209840127e620e&parent_id=_1790226_1&course_id=_306327_1&am_course_id=193484&ver=7&content_id=_2005208_1",
                        },
                    ],
                },
                {
                    "type": "folder",
                    "name": "Tut8 video",
                    "children": [
                        {
                            "type": "recorded_lecture",
                            "name": "Tut8 _ _1_tut8_1",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=studiofca1e4e07f7e2d657da86dcbf3&parent_id=_1790224_1&course_id=_306327_1&am_course_id=196398&ver=7&content_id=_2035416_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut8 _ _2_tut8_2",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=studiof124ab148b05980e3e6a2cc495&parent_id=_1790224_1&course_id=_306327_1&am_course_id=196399&ver=7&content_id=_2035419_1",
                        },
                        {
                            "type": "recorded_lecture",
                            "name": "Tut8 _ _3_tut8_3",
                            "predownload_link": "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=studiod9822d86548d744043319e3606&parent_id=_1790224_1&course_id=_306327_1&am_course_id=196400&ver=7&content_id=_2035421_1",
                        },
                    ],
                },
                {
                    "type": "folder",
                    "name": "Tutorial 1 to tutorial 10",
                    "children": [
                        {
                            "type": "file",
                            "name": "Tut1_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478986_1/xid-9478986_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut2_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478990_1/xid-9478990_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut3_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478997_1/xid-9478997_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut4_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479001_1/xid-9479001_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut5_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479005_1/xid-9479005_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut6_CE2003_No_Tut",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479009_1/xid-9479009_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut7_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479010_1/xid-9479010_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut8_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-10950982_1/xid-10950982_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut9_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479022_1/xid-9479022_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut10_CE2003",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478982_1/xid-9478982_1",
                        },
                    ],
                },
                {
                    "type": "folder",
                    "name": "Tutorial solutions",
                    "children": [
                        {
                            "type": "file",
                            "name": "Tut1_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875202-dt-content-rid-9478989_1/xid-9478989_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut2_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875203-dt-content-rid-9478994_1/xid-9478994_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut3_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875204-dt-content-rid-9478999_1/xid-9478999_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut4_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875205-dt-content-rid-9479003_1/xid-9479003_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut5_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875206-dt-content-rid-9479007_1/xid-9479007_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut7_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875207-dt-content-rid-9479012_1/xid-9479012_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut8_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875208-dt-content-rid-10950997_1/xid-10950997_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut9_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875209-dt-content-rid-9479024_1/xid-9479024_1",
                        },
                        {
                            "type": "file",
                            "name": "Tut10_CE2003_soln",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875210-dt-content-rid-9478985_1/xid-9478985_1",
                        },
                        {
                            "type": "file",
                            "name": "tut10_alt_answerQ2",
                            "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875211-dt-content-rid-9478981_1/xid-9478981_1",
                        },
                        {
                            "type": "folder",
                            "name": "Soln to Mod 1 exercise",
                            "children": [
                                {
                                    "type": "file",
                                    "name": "Mod1_Homework_soln",
                                    "predownload_link": "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1980456-dt-content-rid-10080708_1/xid-10080708_1",
                                }
                            ],
                        },
                    ],
                },
            ],
        }

        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = folder.serialize(BbRouter)
            self.assertDictEqual(expected, result)
