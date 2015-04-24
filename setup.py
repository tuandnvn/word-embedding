from setuptools import setup, find_packages, Extension

extensions = [Extension("wordembedding", ["wordembedding"])]

setup(
    name='word-embedding',
    version='0.0.1',
    description=('Working with embedding'),
    packages=["wordembedding"],
    install_requires=['numpy'],
    author='Tuan Do',
    url='https://github.com/tuandnvn/word-embedding',
    license='Apache 2.0',
    classifiers=['Development Status :: 1'],
    ext_modules=extensions
)
