# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as file:
    desc = file.read()

setup(
    name='backpyf_binance',
    version='0.1.6a2',
    packages=find_packages(),
    description='This module connects your BackPy strategy with the real market using binance.',
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Diego',
    url='https://github.com/Diego-Cores/BackPy-binance-connector',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'binance-futures-connector==4.1.0',
        'pandas>=1.3.0',
        'numpy>=1.16.5',
    ],
    extras_require={
        'backpyf': [
            'backpyf @ git+https://github.com/diego-cores/BackPy.git@main',
        ],
        'optional': [
            'python-telegram-bot>=21.11.1',
    ]}
)
