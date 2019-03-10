"""Setup Ax for pip"""

import pathlib
from setuptools import setup, find_packages

# The directory containing this file
here = pathlib.Path(__file__).parent

# The text of the README file
readme = (here / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ax",
    version="0.0.1",
    description="Ax workflow apps builder",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/enf644/ax",
    author="Mikhail Marenov",
    author_email="enf644@gmail.com",
    license="COMMERCIAL",
    classifiers=[
        "License :: Commercial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'sanic>=18.12.0',
        'Sanic-GraphQl>=1.0.2',
        'Sanic-Cors>=0.9.7',
        'SQLAlchemy>=1.2.12',
        'sqlalchemy-utils>=0.33.9',
        'alembic>=1.0.8',
        'graphene>=2.1.3',
        'graphene-sqlalchemy>=2.1.0',
        'graphql-core>=2.1',
        'graphql-relay>=0.4.5',
        'graphql_ws>=0.3.0',
        'aiocache[redis]>=0.10.1',
        'aiopubsub>=2.1.5',
        'APScheduler>=3.5.3',
        'pyyaml>=3.13',
        'typing>=3.6.6',
        'ujson>=1.35',
        'loguru>=0.2.5',
    ],
    entry_points={
        "console_scripts": [
            'ax = app:main',
        ]
    },
)
