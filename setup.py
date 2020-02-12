from setuptools import setup, find_packages


setup(
    name='datasette-cldf',
    version='0.1.0',
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    description='datasette plugin to explore CLDF datasets',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='',
    license='Apache 2.0',
    url='https://github.com/cldf/datasette-cldf',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "datasette": ["cldf = datasette_cldf"],
        'cldfbench.commands': ['datasette=datasette_cldf.commands'],
    },
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        "datasette>=0.32",
        'datasette-template-sql',
        'datasette-cluster-map',
        'pycldf>=1.11.0',
        'cldfbench',
        'clldutils',
        'jinja2',
        'uritemplate',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'mock',
            'asgiref',
            'pytest>=4.3',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
