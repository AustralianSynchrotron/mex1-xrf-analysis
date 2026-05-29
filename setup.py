from setuptools import setup, find_packages

setup(
    name='xrf-analysis',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'h5py',
        'xraylib',
    ],
    entry_points={
        'console_scripts': [
            'xrf-analyze=xrf_analysis.cli:main',
        ],
    },
)
