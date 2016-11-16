"""Setup script for Shisetsu
"""

from distutils.core import setup

from pip.req import parse_requirements
from pip.download import PipSession

VERSION = '0.1.3'

REQUIREMENTS = [str(req) for req in parse_requirements(
    'requirements.txt',
    session=PipSession())]

setup(
    name='Shisetsu',
    version=VERSION,
    description='An RPC-like protocol on top of Redis',
    author='Kix Panganiban',
    author_email='kixpanganiban@protonmail.com',
    url='https://github.com/KixPanganiban/Shisetsu',
    packages=['shisetsu'],
    install_requires=REQUIREMENTS,
    license='MIT',
    )
