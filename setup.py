"""Setup Ax for pipy"""

import pathlib
import yaml
from setuptools import setup

# The directory containing this file
here = pathlib.Path(__file__).parent

# The text of the README file
readme = (here / "README.md").read_text()


def get_version():
    """Get ax version from app.yaml"""
    with open(str(here / 'ax' / 'app.yaml')) as yaml_file:
        app_yaml = yaml.load(yaml_file)
        return app_yaml['env_variables']['AX_VERSION']


def get_requirements():
    """Create list of required packages from requirements.txt. No versions ."""
    requires = []
    with open('ax/requirements.txt') as file:
        lines = file.read().splitlines()
        for line in lines:
            if not line.startswith('#') and line.strip() != '':
                package_name, version = line.split('==')
                del version
                requires.append(package_name)
    return requires


# This call to setup() does all the work
setup(
    name="ax",
    version=get_version(),
    description="Ax workflow apps builder",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/enf644/ax",
    author="Mikhail Marenov",
    author_email="enf644@gmail.com",
    license="COMMERCIAL",
    classifiers=[
        "License :: Other/Proprietary License",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning"
    ],
    packages=['ax'],
    zip_safe=False,
    include_package_data=True,
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            'ax = ax.main:main',
        ]
    },
)
