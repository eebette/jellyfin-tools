from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from install import fix_install


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        fix_install.install_dll()
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        fix_install.install_dll()
        install.run(self)


setup(
    name="Jellyfin-Tools",
    version="0.0.0.1",
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
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    entry_points={"console_scripts": ["jellyfin-cover=cli.cli:main"]},
)
