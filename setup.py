from setuptools import setup

setup(
    name='songs',
    packages=['songs'],
    include_package_data=True,
    install_requires=[
        'flask', 'pymongo', 'flask_pymongo',
    ],
)