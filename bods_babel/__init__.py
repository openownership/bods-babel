TRANSLATABLE_CODELIST_HEADERS = ('title', 'description', 'technical note')
TRANSLATABLE_SCHEMA_KEYWORDS = ('title', 'description')

def text_to_translate(value, condition=True):
    if condition and isinstance(value, str):
        return value.strip()