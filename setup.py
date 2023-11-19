from setuptools import setup, find_packages

with open("package/README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name='downgit',
    version='2.0',
    author = "Propsi4",
    author_email = "gaenday12@gmail.com",
    description = "Download any subdirectory or file from GitHub repository",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Propsi4/DownGitCMD",
    license='MIT',
    keywords=['downgit','download exact repo', 'github', 'download folder from repo', 'download file from repo'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'downgit = package.downgit:main',
        ],
    },
    install_requires=[
    'certifi>=2023.7.22',
    'charset-normalizer>=3.3.2',
    'colorama>=0.4.6',
    'idna>=3.4',
    'requests>=2.31.0',
    'tqdm>=4.66.1',
    'urllib3>=2.0.7',
    ],
)
