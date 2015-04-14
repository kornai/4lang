from setuptools import setup, find_packages

setup(
    name='fourlang',
    version='1.0',
    description='mapping natural language to concept networks for computational semantics',  # nopep8
    url='https://github.com/kornai/pymachine',
    author='Gabor Recski',
    author_email='recski@mokk.bme.hu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='semantics nlp',

    package_dir={'': 'src'},
    packages=find_packages("src"),

    dependency_links=[
        "https://github.com/kornai/pymachine/tarball/master#egg=pymachine"],
    install_requires=[
        "nltk", "pymachine", "requests", "stemming", "unidecode"],
)
