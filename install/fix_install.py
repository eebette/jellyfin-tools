#!/usr/bin/python3

# Standard library imports
import http.client
import io
import os
import shutil
import sys
import zipfile
from urllib.request import urlopen
from typing import IO

# Other package imports
from PIL import features

# Local imports
from .config import Dll


def check_dll():
    """
    Portable checker requiring user confirmation for dll installation.
    """
    if not features.check('raqm'):
        if input("libraqm and/or fribidi dll's are not found! This package will not work without these dll's. "
                 "Install them now? [Y/n]").lower() in ["", "y"]:
            install_dll()
        else:
            print("Skipping install. Library cover CLI functionality may return error.")


def get_dll(url: str = Dll.URL.value) -> bytes:
    """
    Gets the dll file from the provided URL and loads into memory.
    :param url: The URL string of the dll.
    :return: Binary file in memory of downloaded zip file containing dll's
    """
    response: http.client.HTTPResponse = urlopen(url)
    file: bytes = response.read()
    return file


def extract_zip_to_dir(file, target_directory, path_hint) -> None:
    """
    Extracts the files (not directories) of an in-memory zip file to a target directory, matching/filtering a provided
    path substring.
    :param file: The file-like zip object to extract from.
    :param target_directory: The target directory to send the files to.
    :param path_hint: The path substring filter to match against while extracting.
    """
    # Re-encode bytes object to IO for compatibility
    zip_file: io.BytesIO = io.BytesIO(file)

    # Open zip file for reading/extracting
    with zipfile.ZipFile(zip_file, "r") as zip_directory:

        # Loop over files in zip file
        for nested_file in zip_directory.namelist():

            # Get file name from path
            file_name: str = os.path.basename(nested_file)

            # Skip this file/loop iteration if file (1) isn't a .dll and (2) doesn't match the path hint filter
            if (not file_name.endswith(".dll")) or (not f"/{path_hint}/" in nested_file):
                continue

            # Open the file from the zip as source
            source: IO = zip_directory.open(nested_file)

            # Open the target directory
            target: IO = open(os.path.join(target_directory, file_name), "wb")

            # Write source file to target directory
            with source, target:
                shutil.copyfileobj(source, target)


def get_python_directory() -> str:
    """
    Gets the directory of the default python program
    :return: The path of the directory containing the default Python executable
    """
    python_location: str = shutil.which("python")
    python_directory: str = os.path.dirname(python_location)
    return python_directory


def check_is_64_bit() -> bool:
    """
    Checks if the currently running system is 64-bit architecture.
    :return: Boolean TRUE if the architecture is detected as 64-bit, otherwise FALSE.
    """
    is_64_bit: bool = sys.maxsize > 2 ** 32
    return is_64_bit


def get_architecture_path_hint(is_64_bit: bool) -> str:
    """
    Gets a path substring based on directory naming conventions for 64-bit or 32-bit architectures.
    :param is_64_bit: Boolean value for if the return value should be for 64- or non-64-bit architectures.
    :return: String representation of directory naming convention used for provided architecture.
    """
    if is_64_bit:
        path_hint: str = "x64"
    else:
        path_hint: str = "x86"
    return path_hint


def install_dll() -> None:
    """
    Installs the dlls needed by Pillow on Windows for certain features.
    """
    if features.check('raqm'):
        print("libraqm and/or fribidi dlls already installed. Nothing to do here!")

    else:
        # Download the dll archive
        dll = get_dll()
        print("dll archive downloaded successfully.")

        # Check system architecture
        is_sys_64_bit = check_is_64_bit()
        print(f"System is 64-bit: {is_sys_64_bit}")

        # Get path hint for filtering dll archive
        sys_architecture = get_architecture_path_hint(is_sys_64_bit)
        print(f"Will filter for dlls for architecture type: {sys_architecture}")

        # Detect default Python directory
        python_directory = get_python_directory()
        print(f"Default Python directory detected at: {python_directory}")

        # Extract the downloaded dll's to the Python directory
        print("Extracting the downloaded dll's to the Python directory...")
        extract_zip_to_dir(dll, python_directory, sys_architecture)
        print("Installation Done! Please run your command again.")
        exit(0)


def main() -> None:
    check_dll()


if __name__ == "__main__":
    main()
