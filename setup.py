import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'Flask',
    'flask-restx',
    'sqlalchemy-filters',
    'werkzeug',
    'sqlalchemy',
    'deepmerge',
    'flask-jwt-extended[asymmetric_crypto]'
]

setuptools.setup(
    name='flask-api-utils',
    version='1.4.0',
    author="Tuan Nguyen",
    author_email="tuan.nguyen@groovetechnology.com",
    install_requires=requirements,
    packages=setuptools.find_packages()
)
