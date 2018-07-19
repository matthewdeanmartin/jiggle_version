# coding=utf-8
"""
Upgrade damaged to sem.ver
"""
from jiggle_version.schema_guesser import version_object_and_next


def test_various():
    for ver in ['0.1','1','1.3a1']:
        v, vnext, schema = version_object_and_next(ver)
        assert v, ver
        assert vnext, ver
