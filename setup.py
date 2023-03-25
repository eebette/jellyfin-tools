from setuptools import setup, find_packages

setup(
    name="Jellyfin-Tools",
    version="1.0.0",
    packages=find_packages(include=["cli", "cli.fonts", "install"]),
    package_data={"": ["Prima Sans Bold.otf"]},
    url="https://github.com/eebette/Jellyfin-Tools",
    license="LICENSE.txt",
    author="Eric Bette",
    author_email="eric.bette@pm.me",
    description="Scripted tools for helping manage a Jellyfin library.",
    install_requires=[
        "numpy",
        "Pillow",
        "fonttools",
        "opencv-contrib-python"
    ],
    entry_points={"console_scripts": ["jellyfin-cover=cli.cli:main"]},
)

