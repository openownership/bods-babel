import os
import csv
import gettext
import json
import logging
from glob import glob
from tempfile import TemporaryDirectory

from bods_babel.translate import translate

codelist = """code,title,description,technical note
direct,Direct,"The interest is held directly.",
indirect,Indirect,"The interest is held through one or more intermediate entities (including arrangements).",
unknown,Unknown,"The interest may be direct or indirect.","This is a note."
"""  # noqa

schema = """{
  "id": "person-statement.json",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "version": "0.1",
  "type": "object",
  "title": "Person statement",
  "description": "A person statement describes the information known about a natural person at a particular point in time, or from a given submission of information",
  "properties": {
        "statementID": {
          "$ref": "components.json#/definitions/ID",
          "propertyOrder": 1
        },
      "statementType": {
            "title": "Statement type",
          "description": "This should always be 'personStatement'.",
          "type": "string",
          "enum": [
              "personStatement"
          ],
          "propertyOrder": 2,
          "openCodelist": false,
          "codelist": "statementType.csv"
        },
      "statementDate": {
            "$ref": "components.json#/definitions/StatementDate",
          "propertyOrder": 3
        },
      "personType": {
            "title": "Person type",
          "description": "Use the [personType codelist](#persontype). The ultimate beneficial owner of a legal entity is always a natural person. Where the beneficial owner has been identified, but information about them cannot be disclosed, use 'anonymousPerson'. Where the beneficial owner has not been clearly identified, use 'unknownPerson'. Where the beneficial owner has been identified use knownPerson.",
          "type": "string",
          "enum": [
              "anonymousPerson",
            "unknownPerson",
            "knownPerson"
          ],
          "propertyOrder": 4,
          "codelist": "personType.csv",
          "openCodelist": false
        }
      }
}"""  # noqa


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
                'The interest is held through one or more intermediate entities (including arrangements).': 'Intermediate entities (including russian) but in russian.',  # noqa
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
                (glob(os.path.join(sourcedir, '*.csv')), builddir,
                    'codelists'), ], '', 'fake_ru')

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
        'description but in russian': 'Intermediate entities (including russian) but in russian.',  # noqa
        'title but in russian': 'indirect but in russian'
    }, {
        'code but in russian': 'unknown',
        'note but in russian': 'This is a russian note.',
        'description but in russian': 'Direct or indirect but in russian.',
        'title but in russian': 'unknown but in russian',
    }]

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to fake_ru using "codelists" domain, into {}'.format(  # noqa
        builddir)


def test_translate_schema(monkeypatch, caplog):
    class Translation(object):
        def __init__(self, *args, **kwargs):
            pass

        def gettext(self, *args, **kwargs):
            return {
                "Person statement": "Person statement but Russian",
                "A person statement describes the information known about a natural person at a particular point in time, or from a given submission of information": "Russian person statement description",  # noqa
                "Statement type": "Statement type but Russian",
                "This should always be 'personStatement'.": "Russian this should always be Russian personStatement.",  # noqa
                "Person type": "Person type but Russian",
                "Use the [personType codelist](#persontype). The ultimate beneficial owner of a legal entity is always a natural person. Where the beneficial owner has been identified, but information about them cannot be disclosed, use 'anonymousPerson'. Where the beneficial owner has not been clearly identified, use 'unknownPerson'. Where the beneficial owner has been identified use knownPerson.": "Russian use the [russian personType](#persontype). The ultimate russian russian..",  # noqa
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'person-statement.json'), 'w') as f:
            f.write(schema)

        with open(os.path.join(sourcedir, 'untranslated.json'), 'w') as f:
            f.write(schema)

        with TemporaryDirectory() as builddir:
            translate([
                ([os.path.join(sourcedir, 'person-statement.json')],
                 builddir, 'schema'),
            ], '', 'fake_ru', version='1.1')

            with open(os.path.join(builddir, 'person-statement.json')) as f:
                data = json.load(f)

            assert not os.path.exists(
                os.path.join(builddir, 'untranslated.json'))

    assert data == {
        "id": "person-statement.json",
        "$schema": "http://json-schema.org/draft-04/schema#",
        "version": "0.1",
        "type": "object",
        "title": "Person statement but Russian",
        "description": "Russian person statement description",
        "properties": {
            "statementID": {
              "$ref": "components.json#/definitions/ID",
              "propertyOrder": 1
            },
            "statementType": {
                "title": "Statement type but Russian",
                "description": "Russian this should always be Russian personStatement.",  # noqa
                "type": "string",
                "enum": [
                    "personStatement"
                ],
                "propertyOrder": 2,
                "openCodelist": False,
                "codelist": "statementType.csv"
            },
            "statementDate": {
                "$ref": "components.json#/definitions/StatementDate",
                "propertyOrder": 3
            },
            "personType": {
                "title": "Person type but Russian",
                "description": "Russian use the [russian personType](#persontype). The ultimate russian russian..",  # noqa
                "type": "string",
                "enum": [
                    "anonymousPerson",
                    "unknownPerson",
                    "knownPerson"
                ],
                "propertyOrder": 4,
                "codelist": "personType.csv",
                "openCodelist": False
            }
        }
    }

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to fake_ru using "schema" domain, into {}'.format(  # noqa
        builddir)
