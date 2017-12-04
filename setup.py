from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = ''.join(f.readlines())


setup(
    name='labelord_tomikeKrasnay',
    version='0.5.0',
    description='Global multi-project management of GitHub labels',
    long_description=long_description,
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    maintainer='Tomáš Krasnay',
    maintainer_email='krasntom@fit.cvut.cz',
    keywords='github,labels,cli,web',
    license='Public Domain',
    url='https://github.com/TomikeKrasnay',
    python_requires='~=3.6',
    packages=find_packages(),
    package_data={'labelord': ['templates/*.html', 'static/*.css']},
    install_requires=['click>=6.7', 'Flask>=0.12.2', 'requests>=2.18.4'],
    entry_points={
        'console_scripts': [
            'labelord = labelord.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Utilities',
        ],
    zip_safe=False,
)