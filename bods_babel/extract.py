from bods_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS, text_to_translate

def clean_text(text):
    if isinstance(text, str):
        return text.strip()


def extract_codelist(fileobj, keywords, comment_tags, options):
    """
    Yields each header, and the title, description and technical note values of a codelist CSV file.
    """

    # Use universal newlines mode, to avoid parsing errors.
    reader = csv.DictReader(StringIO(fileobj.read().decode(), newline=''))
    for fieldname in reader.fieldnames:
        if fieldname:
            yield 0, '', fieldname, ''

    for lineno, row in enumerate(reader, 1):
        for key, value in row.items():
            text = text_to_translate(value, key in TRANSLATABLE_CODELIST_HEADERS)
            if text:
                yield lineno, '', text, [key]


def extract_schema(fileobj, keywords, comment_tags, options):
    """
    Yields the "title" and "description" values of a JSON Schema file.
    """
    def _extract_schema(data, pointer=''):
        if isinstance(data, list):
            for index, item in enumerate(data):
                yield from _extract_schema(item, pointer='{}/{}'.format(pointer, index))
        elif isinstance(data, dict):
            for key, value in data.items():
                text = text_to_translate(value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    yield text, '{}/{}'.format(pointer, key)

    data = json.loads(fileobj.read().decode())
    for text, pointer in _extract_schema(data):
        yield 1, '', text, [pointer]