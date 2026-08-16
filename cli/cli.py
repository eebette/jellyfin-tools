# Standard library imports
import argparse
import os
import sys
import traceback

# Local imports
from cli.config import Params
from cli.image import create_library_image


def run(args):
    """
    Calls `create_library_image` for each respective image and library title pair.
    :param args: The argparse args to use for this function.
    """

    # The number of image args must match the number of title args.()
    assert len(args.image) == len(args.title)

    # Fail early with a clear message if the provided font file doesn't exist.
    if args.font and not os.path.isfile(args.font):
        print(f"Font file not found: {args.font}", file=sys.stderr)
        sys.exit(1)

    # The shadow opacity should be clamped between 0 and 1.
    args.shadow = max(0, min(1, args.shadow))
    for t, i in enumerate(args.image):
        title = args.title[t]
        output = create_library_image(
            file=i,
            library_name=title,
            destination=args.destination,
            shadow=args.shadow,
            font=args.font,
        )
        print(f"Generated image to: {output}")


def main():
    """
    Entry point into the CLI.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        "jellyfin-tools",
        description="Command line tool for generating library covers consistent with Jellyfin and Emby's styling.",
    )

    parser.add_argument(
        "--verbose", "-v", help="Enable verbose logging", action="count", default=0
    )

    subparser = parser.add_subparsers(
        title="subparsers", dest="command", required=True
    )

    cover_parser = subparser.add_parser("cover")

    cover_subparser = cover_parser.add_subparsers(
        title="subparsers", dest="cover_command", required=True
    )

    create_parser = cover_subparser.add_parser("create")
    create_parser.set_defaults(func=run)

    create_parser.add_argument(
        "--image", dest="image", action="store", nargs="+", required=True
    )

    create_parser.add_argument(
        "--title", dest="title", action="store", nargs="+", required=True
    )

    create_parser.add_argument(
        "--destination",
        dest="destination",
        action="store",
        type=str,
        default=str(),
    )

    create_parser.add_argument(
        "--shadow",
        dest="shadow",
        action="store",
        type=float,
        default=Params.FOREGROUND_WEIGHT.value,
    )

    create_parser.add_argument(
        "--font",
        dest="font",
        action="store",
        type=str,
        default=None,
        help="Path to a font file (.ttf/.otf) to use for the title text instead of the bundled Prima Sans Bold",
    )

    # Parse the args
    args = parser.parse_args()

    # Try calling the appropriate handler
    if hasattr(args, "func") and args.func:
        try:
            args.func(args)
        except Exception as e:
            # Print the full traceback when --verbose is set
            if args.verbose:
                traceback.print_exc()
            print(f"Encountered an error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Both subparser levels are required, so argparse errors out before this
        # branch can normally be reached; kept as a safe fallback.
        parser.print_help()


if __name__ == "__main__":
    main()
