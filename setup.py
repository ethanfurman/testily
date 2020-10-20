try:
    import setuptools
    setuptools
except ImportError:
    pass
from distutils.core import setup

py2_only = ()
py3_only = ()
make = []

data = dict(
        name='testily',
        version='0.0.0',
        license='BSD License',
        description='various tools to help with testing',
        long_description='various tools to help with testing',
        url='https://github.com/ethanfurman/testily',
        packages=['testily', ],
        package_data={
           'testily' : [
               'LICENSE',
	           'WHATSNEW',
               ],
           },
        provides=['testily'],
        install_requires=[],
        author='Ethan Furman',
        author_email='ethan@stoneleaf.us',
        classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Database',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            ],
        )

if __name__ == '__main__':
    setup(**data)

