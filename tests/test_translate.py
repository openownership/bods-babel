import os
import csv
import gettext
import logging
from glob import glob
from tempfile import TemporaryDirectory

from bods_babel.translate import translate

codelist = """code,title,description,technical note
direct,Direct,"The interest is held directly.",
indirect,Indirect,"The interest is held through one or more intermediate entities (including arrangements).",
unknown,Unknown,"The interest may be direct or indirect.","This is a note."
"""  # noqa


def test_translate_codelists(monkeypatch, caplog):
    class Translation(object):
        def __init__(self, *args, **kwargs):
            pass

        def gettext(self, *args, **kwargs):
            return {
                'code': 'code but in russian',
                'title': 'title but in russian',
                'description': 'description but in russian',
                'technical note': 'note but in russian',
                'Direct': 'direct but in russian',
                'Indirect': 'indirect but in russian',
                'Unknown': 'unknown but in russian',
                'The interest is held directly.': 'Held directly but in russian.',  # noqa
                'The interest is held through one or more intermediate entities (including arrangements).': 'Intermediate entities (including russian) but in russian.',
                'The interest may be direct or indirect.': 'Direct or indirect but in russian.',  # noqa
                'This is a note.': 'This is a russian note.',
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'interestLevel.csv'), 'w') as f:
            f.write(codelist)

        with TemporaryDirectory() as builddir:
            translate([
                (glob(os.path.join(sourcedir, '*.csv')), builddir, 'codelists'),
            ], '', 'fake_ru')

            with open(os.path.join(builddir, 'interestLevel.csv')) as f:
                rows = [dict(row) for row in csv.DictReader(f)]

    assert rows == [{
        'code but in russian': 'direct',
        'description but in russian': 'Held directly but in russian.',
        'note but in russian': '',
        'title but in russian': 'direct but in russian'
    }, {
        'code but in russian': 'indirect',
        'note but in russian': '',
        'description but in russian': 'Intermediate entities (including russian) but in russian.',
        'title but in russian': 'indirect but in russian'
    }, {
        'code but in russian': 'unknown',
        'note but in russian': 'This is a russian note.',
        'description but in russian': 'Direct or indirect but in russian.',
        'title but in russian': 'unknown but in russian',
    }]

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to fake_ru using "codelists" domain, into {}'.format(
        builddir)


def test_translate_schema():
    pass
