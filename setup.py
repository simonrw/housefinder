from setuptools import setup, find_packages

setup(
    name='housefinder',
    version='0.0.1',
    author='Simon Walker',
    packages=find_packages(exclude=[]),
    author_email='s.r.walker101@googlemail.com',
    install_requires=[
        'requests',
        'sqlalchemy',
        'psycopg2',
    ],
    license='MIT',
    entry_points={
        'console_scripts': [
            'housefinder=housefinder.api:main',
        ]
    },
)
