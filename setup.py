from setuptools import setup

setup(
    name='bw2parameters',
    version="0.6.5",
    packages=["bw2parameters"],
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE').read(),
    url="https://bitbucket.org/cmutel/brightway2-parameters",
    install_requires=[
        "asteval",
        "astunparse",
        "numpy",
        "stats_arrays",
    ],
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
