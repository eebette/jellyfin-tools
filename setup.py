from setuptools import setup, find_packages

setup(
    name="Jellyfin-Tools",
    version="0.0.0.1",
    packages=find_packages(include=["cli", "cli.fonts"]),
    package_data={"": ["Prima Sans Bold.otf"]},
    url="",
    license="",
    author="eric",
    author_email="",
    description="",
    entry_points={"console_scripts": ["jellyfin-cover=cli.cli:main"]},
)
