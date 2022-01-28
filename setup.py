from setuptools import setup


SHORT_DESCRIPTION = 'Nuclino API wrapper'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='PyNuclino',
    python_requires='>=3.5',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='0.1.1',
    author='Daniel Minukhin',
    author_email='ddddsa@gmail.com',
    url='https://github.com/Vanderhoof/PyNuclino',
    packages=['nuclino'],
    license='MIT',
    platforms='any',
    install_requires=[
        'ratelimit',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ]
)
