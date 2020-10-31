import unittest
from unittest.mock import patch

from ntu_learn_downloader.tests.mock_server import MOCK_CONSTANTS
from ntu_learn_downloader import (
    get_courses,
    get_content_ids,
    get_recorded_lecture_download_link,
    get_file_download_link,
)

from ntu_learn_downloader.api import get_contents
from ntu_learn_downloader.models import Folder, Doc, RecordedLecture

BbRouter = "expires:1583963361,id:1A633268311FA435A6HT7K968346A658,signature:bqguvcoi0nh434robmpzervdtpomolh17rk3m9kxhiy0ozd5tzquhd0e4igldygm,site:5ecaf6aa-60ca-4431-89e7-6ed4c720440d,timeout:10800,user:6itk73437hq6tbcznl60t354qc2vn2py,v:2,xsrf:y3d3nzrg-c301-4455-a5a3-hpjdect1jyil"


class TestAPI(unittest.TestCase):
    def test_get_courses(self):
        expected_result = [
            ("19S2-MAE-MA1002-FUNDAMENTAL ENG MATERIALS", "305884_1"),
            ("19S2-MAE-MA2079-ENG INNOVATION & DESIGN", "305901_1"),
            ("19S2-MAE-MA1002-FUNDAMENTAL ENG MATERIALS (TUT) - MA4", "316098_1"),
            ("19S2-MAE-MA2006-ENGINEERING MATHEMATICS*", "305894_1"),
            ("19S2-MAE-MA1001-DYNAMICS*", "305883_1"),
            ("19S2-MAE-MA2005-ENGINEERING GRAPHICS*", "305893_1"),
            ("19S2-MAE-MA2006-ENGINEERING MATHEMATICS (TUT) MA11", "316929_1"),
            ("19S2-MAE-MA2011-MECHATRONICS SYS INTERFACING*", "305898_1"),
            ("19S2-MAE-MA2071-LABORATORY EXPERIMENTS (ME) (LAB)", "305900_1"),
            (
                "19S2-MAE-MA2071-LABORATORY EXPERIMENTS for E2.11 and E2.12 - MONDAY group",
                "315515_1",
            ),
            ("Basic Safety Training", "298503_1"),
            ("LIB-IML_AY2019: Information & Media Literacy (AY2019/20)", "302013_1"),
            ("OHS2SIG01 - Understanding Signage from SS508 (by e-learning)", "35674_1"),
            ("PH1012-PHYSICS A", "303535_1"),
            ("SGSECURE ï¿½ Prepared Citizen Training", "169228_1"),
            ("Student Life Modules", "302307_1"),
        ]
        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_courses(BbRouter)

            expected = set(expected_result)
            got = set(result)
            self.assertSetEqual(expected, got)

    def test_get_content_ids(self):
        expected_result = [
            ("Content", "_1643678_1"),
            ("19S1 Recorded Lectures", "_1643676_1"),
        ]
        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_content_ids(BbRouter, "_302242_1")

            expected = set(expected_result)
            got = set(result)
            self.assertSetEqual(expected, got)

    def test_get_recorded_lecture_download_link(self):
        expected_url = "https://ntucee.ntu.edu.sg/content/0090842a4023a822af16c4160f6a4e95/s2001140130007cad14c2533d8829926b8e1847e39b41/media/1.mp4"
        predownload_link = "/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=s2001140130007cad14c2533d8829926b8e1847e39b41&parent_id=_1790232_1&course_id=_306329_1&am_course_id=189561&ver=7&content_id=_1924894_1"
        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            url = get_recorded_lecture_download_link(BbRouter, predownload_link)
            self.assertEqual(url, expected_url)

    def test_get_file_download_link(self):
        """
        actual file object: https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875202-dt-content-rid-9478989_1/xid-9478989_1
        from 19S2-CE2003-DIGITAL SYSTEMS DESIGN / Content / Tutorials / Tutorial solutions / Tut1_CE2003_soln
        """
        expected_url = "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875202-dt-content-rid-9478989_1/courses/19S2-CE2003-LEC/Tut1_CE2003_soln.pdf"
        link = "https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875202-dt-content-rid-9478989_1/xid-9478989_1"
        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_file_download_link(BbRouter, link)
            self.assertEqual(expected_url, result)


class InternalTestAPI(unittest.TestCase):
    def test_get_contents_1(self):
        # "https://ntulearn.ntu.edu.sg/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1790226_1"
        expected = [
            Folder(
                name="Lectures",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875189_1",
                details="This folder contains the lecture slides,\xa0the example class slides,\xa0and\xa0the\xa0on-line (LAMS) lectures",
            ),
            Folder(
                name="Tutorials",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875198_1",
                details="Tutorials for the whole course. Solutions are uploaded towards the end of semester. Tutorials commence in Week 2.",
            ),
            Folder(
                name="Labs",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875212_1",
                details="Lab instructions for the 5 labs across the whole semester. See Lab schedule (in Information) for lab timing.",
            ),
            Folder(
                name="Previous Quiz Papers",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875224_1",
                details="The quiz will cover material in the first 4 modules (tutorial 1 to 4).\xa0\nSee the course schedule for the timing of\xa0this semester's quiz.",
            ),
            Folder(
                name="Past Exam paper Solutions",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875236_1",
                details="This folder contains selected solutions to past CE2003\xa0exam papers.",
            ),
        ]

        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_contents(
                BbRouter,
                "_306327_1",
                "_1790226_1",
            )
            self.assertListEqual(expected, result)

    def test_get_contents_2(self):
        # 19S2-CE2003-DIGITAL SYSTEMS DESIGN Tutorials
        # https://ntulearn.ntu.edu.sg/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875198_1
        expected = [
            Folder(
                name="tut4_video",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1997212_1",
                details="",
                children=None,
            ),
            Folder(
                name="Tut5_video",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_2002442_1",
                details="",
                children=None,
            ),
            Folder(
                name="Tut7_video",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_2005205_1",
                details="",
                children=None,
            ),
            Folder(
                name="Tut8 video",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_2035533_1",
                details="This folder containd\xa0the recorded video for tutorial 8",
                children=None,
            ),
            Folder(
                name="Tutorial 1 to tutorial 10",
                link=None,
                details="",
                children=[
                    Doc(
                        name="Tut1_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478986_1/xid-9478986_1",
                    ),
                    Doc(
                        name="Tut2_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478990_1/xid-9478990_1",
                    ),
                    Doc(
                        name="Tut3_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478997_1/xid-9478997_1",
                    ),
                    Doc(
                        name="Tut4_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479001_1/xid-9479001_1",
                    ),
                    Doc(
                        name="Tut5_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479005_1/xid-9479005_1",
                    ),
                    Doc(
                        name="Tut6_CE2003_No_Tut",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479009_1/xid-9479009_1",
                    ),
                    Doc(
                        name="Tut7_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479010_1/xid-9479010_1",
                    ),
                    Doc(
                        name="Tut8_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-10950982_1/xid-10950982_1",
                    ),
                    Doc(
                        name="Tut9_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9479022_1/xid-9479022_1",
                    ),
                    Doc(
                        name="Tut10_CE2003",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875199-dt-content-rid-9478982_1/xid-9478982_1",
                    ),
                ],
            ),
            Folder(
                name="Tutorial solutions",
                link="/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875200_1",
                details="This folder contains the tutorial solutions",
                children=None,
            ),
        ]

        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_contents(
                BbRouter,
                "_306327_1",
                "_1875198_1",
            )
            self.assertListEqual(expected, result)

    def test_get_contents_3(self):
        """contains item with no img alt
        https://ntulearn.ntu.edu.sg/webapps/blackboard/content/listContent.jsp?course_id=_306329_1&content_id=_1919845_1&mode=reset
        """
        expected = [
            Folder(
                name="Tutorials #1-#10",
                link=None,
                details="",
                children=[
                    Doc(
                        name="T01-T05 SII.pdf",
                        link="/bbcswebdav/pid-1919881-dt-content-rid-9765605_1/xid-9765605_1",
                    ),
                    Doc(
                        name="T06-T10 SII.pdf",
                        link="/bbcswebdav/pid-1919881-dt-content-rid-9765660_1/xid-9765660_1",
                    ),
                ],
            )
        ]

        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_contents(
                BbRouter,
                "_306329_1",
                "_1919845_1",
            )
            self.assertListEqual(expected, result)

    def test_get_contents_4(self):
        # 19S2-CE2003-DIGITAL SYSTEMS DESIGN / Content / Lectures
        # https://ntulearn.ntu.edu.sg/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875189_1
        expected = [
            Folder(
                name="Lecture slides",
                link=None,
                details="",
                children=[
                    Doc(
                        name="1_CE2003_Mod1",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460689_1/xid-9460689_1",
                    ),
                    Doc(
                        name="4_CE2003_Mod1",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460699_1/xid-9460699_1",
                    ),
                    Doc(
                        name="1_CE2003_Mod2",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9687351_1/xid-9687351_1",
                    ),
                    Doc(
                        name="4_CE2003_Mod2",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9687352_1/xid-9687352_1",
                    ),
                    Doc(
                        name="1_CE2003_Mod3",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460693_1/xid-9460693_1",
                    ),
                    Doc(
                        name="4_CE2003_Mod3",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478903_1/xid-9478903_1",
                    ),
                    Doc(
                        name="1_CE2003_Mod4",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460694_1/xid-9460694_1",
                    ),
                    Doc(
                        name="4_CE2003_Mod4",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478904_1/xid-9478904_1",
                    ),
                    Doc(
                        name="1_CE2003_Mod5",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460695_1/xid-9460695_1",
                    ),
                    Doc(
                        name="4_CE2003_Mod5",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478905_1/xid-9478905_1",
                    ),
                    Doc(
                        name="1_CE2003_mod7",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460696_1/xid-9460696_1",
                    ),
                    Doc(
                        name="4_CE2003_mod7",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478906_1/xid-9478906_1",
                    ),
                    Doc(
                        name="New_CE2003_Mod8",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-11036452_1/xid-11036452_1",
                    ),
                    Doc(
                        name="4_CE2003_Mod8",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478907_1/xid-9478907_1",
                    ),
                    Doc(
                        name="1_CE2003_mod9",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9460698_1/xid-9460698_1",
                    ),
                    Doc(
                        name="4_CE2003_mod9",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478908_1/xid-9478908_1",
                    ),
                    Doc(
                        name="CE2003_Mod0",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9512889_1/xid-9512889_1",
                    ),
                    Doc(
                        name="Mod9_Ex2_alternative",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-9478954_1/xid-9478954_1",
                    ),
                    Doc(
                        name="CE2003_EC1_2020.pptx",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-10306479_1/xid-10306479_1",
                    ),
                    Doc(
                        name="CE2003_EC1.pdf",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-10306480_1/xid-10306480_1",
                    ),
                    Doc(
                        name="CE2003_EC2_2020.pptx",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-10406966_1/xid-10406966_1",
                    ),
                    Doc(
                        name="CE2003_EC2.pdf",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-10406967_1/xid-10406967_1",
                    ),
                    Doc(
                        name="CE2003_EC3_2020.pptx",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-10971065_1/xid-10971065_1",
                    ),
                    Doc(
                        name="CE2003_EC3.pdf",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-10971066_1/xid-10971066_1",
                    ),
                    Doc(
                        name="CE2003_EC4_2020.pptx",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-11050827_1/xid-11050827_1",
                    ),
                    Doc(
                        name="CE2003_EC4.pdf",
                        link="https://ntulearn.ntu.edu.sg/bbcswebdav/pid-1875190-dt-content-rid-11050828_1/xid-11050828_1",
                    ),
                ],
            ),
            RecordedLecture(
                name="Mod8_NowControlHazard _ mod8_New_Control hazards",
                predownload_link="/webapps/Acu-AcuLe@rn-BB5dcb73f79ba4c/am/start_play_studio.jsp?sn=studio0578720023632e706a28abb9e8&parent_id=_1790225_1&course_id=_306327_1&am_course_id=196902&ver=7&content_id=_2040766_1",
            ),
        ]
        with patch.dict("ntu_learn_downloader.api.__dict__", MOCK_CONSTANTS):
            result = get_contents(
                BbRouter,
                "_306327_1",
                "_1875189_1",
            )
            self.assertListEqual(expected, result)

    def test_get_contents_5(self):
        # https://ntulearn.ntu.edu.sg/webapps/blackboard/content/listContent.jsp?course_id=_306327_1&content_id=_1875200_1
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
            result = get_contents(
                BbRouter,
                "_306327_1",
                "_1875200_1",
            )
            self.assertListEqual(expected, result)
