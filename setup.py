
from setuptools import setup, find_packages

setup(
    name='backpyf_binance',
    version='0.0.4a1',
    packages=find_packages(),
    description='This module connects your BackPy strategy with the real market using binance.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Diego',
    url='https://github.com/Diego-Cores/BackPy-binance-connector',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'backpyf @ git+https://github.com/diego-cores/BackPy.git@main',
        'binance-futures-connector==4.1.0',
        'pandas>=1.3.0',
        'numpy>=1.16.5',
    ],
    extras_require={
        'optional': [
            'python-telegram-bot>=21.11.1',
    ]}
)
