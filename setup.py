from setuptools import setup, find_packages

setup(
    name='bods-babel',
    version='0.0.1',
    author='Open Ownership',
    url='https://github.com/openownership/bods-babel',
    description='Babel extractors for the Beneficial Ownership Data Standard schema and related components.',
    license='BSD',
    packages=find_packages(),
    long_description=long_description,
    install_requires=[],
    extras_require={
        'test': [
            'coveralls',
            'pytest',
            'pytest-cov',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'babel.extractors': [
            'bods_codelist = bods_babel.extract:extract_codelist',
            'bods_schema = bods_babel.extract:extract_schema',
        ],
    },
)