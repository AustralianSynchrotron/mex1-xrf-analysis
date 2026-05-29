from setuptools import setup, find_packages

setup(
    name='xrf-analysis',
    version='0.1.0',
    packages=[
        'xrf_analysis',
        'xrf_analysis.core',
        'xrf_analysis.visualization',
        'xrf_analysis.dpc',
    ],
    package_dir={
        'xrf_analysis':             'xrf_analysis',
        'xrf_analysis.core':        'core',
        'xrf_analysis.visualization': 'visualization',
        'xrf_analysis.dpc':         'dpc',
    },
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
