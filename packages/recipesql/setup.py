from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'operations for playground databases'

setup(
        name="recipesql",
        version=VERSION,
        author="Israel H.B",
        author_email="<israel.bar.dev@gmail.com>",
        description=DESCRIPTION,
        packages=find_packages(),
        install_requires=['Flask==2.2.2',
                          'flask_sqlalchemy==3.0.3',
                          'psycopg2-binary==2.9.6'],
        keywords=['python', 'database', 'playground', 'postgres', 'recipesql'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
