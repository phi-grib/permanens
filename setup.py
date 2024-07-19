from setuptools import setup, find_packages
setup(
    name='permanens',
    version='0.0.1',
    license='GNU GPLv3 or posterior',
    description='',
    url='https://github.com/phi-grib/permanens',
    download_url='https://github.com/phi-grib/permanens.git',
    author='Manuel Pastor',
    author_email='manuel.pastor@upf.edu',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['permanens=permanens.permanens_scr:main'],
    },
    # If any package contains *.txt or *.rst files, include them:
    package_data={'permanens': ['*.yaml']},
    install_requires=['appdirs']
)
