from setuptools import setup
from cfgdiff import version

setup(
    name="cfgdiff",
    version=version,
    description="diff(1) all your configs",
    author="Evgeni Golov",
    author_email="evgeni@golov.de",
    url="https://github.com/evgeni/cfgdiff",
    license="MIT",
    py_modules=['cfgdiff'],
    scripts=['cfgdiff'],
    zip_safe=False,
    extras_require={
        'XML support': ['lxml'],
        'ConfigObj support': ['ConfigObj'],
        'reconfigure support': ['reconfigure'],
    },
    data_files=[
        ('/usr/share/man/man1', ['cfgdiff.1'])
    ]
)
