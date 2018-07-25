# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'myschool',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = myschool.settings']},
    package_data = {
        'myschool': ['resources/*.csv']
    },
    zip_safe=False,
)
