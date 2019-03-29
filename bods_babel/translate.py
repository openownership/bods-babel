import csv
import gettext
import json
import logging
import os
from collections import OrderedDict
from copy import deepcopy
from io import StringIO

from bods_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS, text_to_translate  # noqa


logger = logging.getLogger('bods_babel')


def translate(configuration, localedir, language, **kwargs):
    """
    Writes files, translating any translatable strings.
    For translated strings in schema files, replaces `{{lang}}` with the language code. Keyword arguments may specify
    additional replacements.
    """
    translators = {}

    for sources, target, domain in configuration:
        logger.info('Translating to {} using "{}" domain, into {}'.format(language, domain, target))

        if domain not in translators:
            translators[domain] = gettext.translation(
                domain, localedir, languages=[language], fallback=language == 'en')

        os.makedirs(target, exist_ok=True)

        for source in sources:
            basename = os.path.basename(source)
            with open(source) as r, open(os.path.join(target, basename), 'w') as w:
                if source.endswith('.csv'):
                    method = translate_codelist
                elif source.endswith('.json'):
                    method = translate_schema
                    kwargs.update(lang=language)
                else:
                    raise NotImplementedError(basename)
                w.write(method(r, translators[domain], **kwargs))


# This should roughly match the logic of `extract_codelist`.
def translate_codelist(io, translator, **kwargs):
    """
    Accepts a CSV file as an IO object, and returns its translated contents in CSV format.
    """
    reader = csv.DictReader(io)

    fieldnames = [translator.gettext(fieldname)
                  for fieldname in reader.fieldnames]
    rows = translate_codelist_data(reader, translator, **kwargs)

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    return io.getvalue()


def translate_codelist_data(source, translator, **kwargs):
    """
    Accepts CSV rows as an iterable object (e.g. a list of dictionaries), and returns translated rows.
    """
    rows = []
    for row in source:
        data = {}
        for key, value in row.items():
            text = text_to_translate(
                value, key in TRANSLATABLE_CODELIST_HEADERS)
            if text:
                value = translator.gettext(text)
            data[translator.gettext(key)] = value
        rows.append(data)
    return rows


# This should roughly match the logic of `extract_schema`.
def translate_schema(io, translator, **kwargs):
    """
    Accepts a JSON file as an IO object, and returns its translated contents in JSON format.
    """
    data = json.load(io, object_pairs_hook=OrderedDict)

    data = translate_schema_data(data, translator, **kwargs)

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)


def translate_schema_data(source, translator, **kwargs):
    """
    Accepts JSON data, and returns translated data.
    """
    def _translate_schema_data(data):
        if isinstance(data, list):
            for item in data:
                _translate_schema_data(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                _translate_schema_data(value)
                text = text_to_translate(
                    value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    data[key] = translator.gettext(text)
                    for old, new in kwargs.items():
                        data[key] = data[key].replace('{{' + old + '}}', new)

    data = deepcopy(source)
    _translate_schema_data(data)
    return data
