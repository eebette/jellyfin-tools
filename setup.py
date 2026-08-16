from setuptools import setup, find_packages

setup(
    name="jellyfin-tools",
    version="1.3.0",
    packages=find_packages(include=["cli", "cli.fonts"]),
    package_data={"": ["Prima Sans Bold.otf"]},
    url="https://github.com/eebette/Jellyfin-Tools",
    license="LICENSE.txt",
    author="Eric Bette",
    author_email="eric.bette@pm.me",
    description="Scripted tools for helping manage a Jellyfin library.",
    install_requires=[
        "setuptools",
        "Pillow>=9.2.0",
    ],
    entry_points={"console_scripts": ["jellyfin-tools=cli.cli:main"]},
)
