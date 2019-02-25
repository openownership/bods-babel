import os
from tempfile import TemporaryDirectory

from bods_babel.extract import extract_codelist, extract_schema

codelist = b"""code,title,description,technical note
  foo  ,  bar  ,  baz  ,  bzz
  bar  ,       ,  bzz  ,  zzz
  baz  ,  bzz  ,       ,  foo
  bzz  ,  zzz  ,  foo  ,       """  # noqa

schema = b"""{
    "title": {
        "oneOf": [{
            "title": "  foo  ",
            "description": "  bar  "
        }, {
            "title": "  baz  ",
            "description": "  bzz  "
        }]
    },
    "description": {
        "title": "  zzz  ",
        "description": "    "
    }
}"""


def assert_result(filename, content, method, expected):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, filename), 'wb') as f:
            f.write(content)

        with open(os.path.join(d, filename), 'rb') as f:
            assert list(method(f, None, None, None)) == expected


def test_extract_codelist():
    assert_result('test.csv', codelist, extract_codelist, [
        (0, '', 'code', ''),
        (0, '', 'title', ''),
        (0, '', 'description', ''),
        (0, '', 'technical note', ''),
        (1, '', 'bar', ['title']),
        (1, '', 'baz', ['description']),
        (1, '', 'bzz', ['technical note']),
        (2, '', 'bzz', ['description']),
        (2, '', 'zzz', ['technical note']),
        (3, '', 'bzz', ['title']),
        (3, '', 'foo', ['technical note']),
        (4, '', 'zzz', ['title']),
        (4, '', 'foo', ['description']),
    ])


def test_extract_codelist_fieldname():
    assert_result('test.csv', b'code,', extract_codelist, [
        (0, '', 'code', ''),
    ])


def test_extract_codelist_newline():
    assert_result('test.csv', b'code\rfoo', extract_codelist, [
        (0, '', 'code', ''),
    ])


def test_extract_schema():
    assert_result('schema.json', schema, extract_schema, [
        (1, '', 'foo', ['/title/oneOf/0/title']),
        (1, '', 'bar', ['/title/oneOf/0/description']),
        (1, '', 'baz', ['/title/oneOf/1/title']),
        (1, '', 'bzz', ['/title/oneOf/1/description']),
        (1, '', 'zzz', ['/description/title']),
    ])
