# Standard library imports
import argparse
import sys

# Local imports
from cli.config import Params
from cli.image import create_library_image
from install import fix_install


def check_fix_dll(func):
    """
    Decorator function for checking the presence of dll's needed for the functionality of the function.
    :param func: The function to wrap.
    """

    def wrapper(*args, **kwargs):
        fix_install.check_dll()
        func(*args, **kwargs)

    return wrapper


@check_fix_dll
def run(args):
    """
    Calls `create_library_image` for each respective image and library title pair.
    :param args: The argparse args to use for this function.
    """

    # The number of image args must match the number of title args.()
    assert len(args.image) == len(args.title)
    # The shadow opacity should be clamped between 0 and 1.
    args.shadow = max(0, min(1, args.shadow))
    t = 0
    for i in args.image:
        title = args.title[t]
        output = create_library_image(file=i, library_name=title, shadow=args.shadow)
        print(f"Generated image to: {output}")
        t += 1


def main():
    """
    Entry point into the CLI.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        "jellyfin-cover",
        description="Command line tool for generating library covers consistent with Jellyfin and Emby's styling.",
    )

    parser.add_argument(
        "--verbose", "-v", help="Enable verbose logging", action="count", default=0
    )

    subparser = parser.add_subparsers(
        title="subparsers", dest="subcommand", required=True
    )

    pipeline_parser = subparser.add_parser("create")
    pipeline_parser.set_defaults(func=run)

    pipeline_parser.add_argument(
        "--image", dest="image", action="store", nargs="+", required=True
    )

    pipeline_parser.add_argument(
        "--title", dest="title", action="store", nargs="+", required=True
    )

    pipeline_parser.add_argument(
        "--shadow", dest="shadow", action="store", type=float, default=Params.FOREGROUND_WEIGHT.value
    )

    # Parse the args
    args = parser.parse_args()

    # Try calling the appropriate handler
    if hasattr(args, "func") and args.func:
        try:
            args.func(args)
        except Exception as e:
            print("Encountered an error: %s", str(e))
            sys.exit(1)
    else:
        eval(args.subcommand + "_parser").print_help()


if __name__ == "__main__":
    main()
