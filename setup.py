from setuptools import setup, find_packages

setup(
    name='housefinder',
    description='Find a house',
    long_description=open('README.md').read(),
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
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
