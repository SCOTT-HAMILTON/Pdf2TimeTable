from setuptools import setup, find_packages

setup(
    name='Pdf2TimeTable',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    py_modules = [ 'timetableparser', 'cli' ],

    install_requires=['tabula-py', 'PyPDF2', 'pandas', 'numpy', 'Click'],

    entry_points='''
        [console_scripts]
        pdf2timetable=Pdf2TimeTable.cli:cli
    ''',

    # metadata to display on PyPI
    author='Scott Hamilton',
    author_email='sgn.hamilton+python@protonmail.com',
    description='Converts a pdf timetable (generated by pronote)  to an excel timetable (that can be used with TimeTable2Header)',
    keywords='timetable pdf parser',
    url='https://github.com/SCOTT-HAMILTON/Pdf2TimeTable',
    project_urls={
        'Source Code': 'https://github.com/SCOTT-HAMILTON/Pdf2TimeTable',
    },
    classifiers=[
        'License :: OSI Approved :: Python Software Foundation License'
    ]
)
