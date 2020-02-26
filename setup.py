import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'Flask',
    'flask-restplus',
    'sqlalchemy-filters',
    'werkzeug',
    'sqlalchemy'
]

setuptools.setup(
    name='api-utils',
    version='0.1',
    author="Tuan Nguyen",
    author_email="tuan.nguyen@groovetechnology.com",
    install_requires=requirements,
    packages=setuptools.find_packages()
)
