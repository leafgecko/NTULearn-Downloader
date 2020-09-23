# Serialized models

# TODO adding gradual typing
# from typing import NamedTuple
from collections import namedtuple

SFolder = namedtuple('SFolder', 'name link details children')
SLecture = namedtuple('SLecture', 'name link')
SDoc = namedtuple('SDoc', 'name link')

