# Standard library imports
import os
import unicodedata
from pathlib import Path
from typing import Optional, Tuple

# Package imports
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

# Local imports
from .config import Params


def get_font_path(
    font_file: str = Params.FONT_FILE.value,
    font_directory: str = Params.FONT_DIRECTORY.value,
    path_to_fonts: str = Path(__file__).parent,
) -> str:
    """
    Gets a path of a given font file within this package.
    :param font_file: The name of the font file to get the path for. Defaults to the Jellyfin library cover font (Prima
    Sans Bold).
    :param font_directory: The parent directory containing the `font_file`. Defaults to the `fonts` folder in this package.
    :param path_to_fonts: The top-level absolute path to `font_dir`. Defaults to the parent directory of this package.
    :return: Absolute path of the font file.
    """
    font_path: str = os.path.join(path_to_fonts, font_directory, font_file)
    return font_path


def write_font_center(
    image: Image.Image,
    size: Tuple[int, int],
    message: str,
    font_path: str,
    font_size: int = Params.FONT_SIZE.value,
    font_color: Tuple[int, int, int, int] = Params.FONT_COLOR.value,
    height_offset: int = Params.HEIGHT_OFFSET.value,
) -> Image.Image:
    """
    Function for writing text in a given font on an image.
    :param image: The image on which to draw text.
    :param size: The width and height (in pixels) of the `image`.
    :param message: The text to write on the image.
    :param font_path: The absolute path to the font to use on the image.
    :param font_size: The size of the font to use. Defaults to manually matched 112 in order to be consistent with
    Jellyfin's library cover styling.
    :param font_color: The RGBA color of the font to use. Defaults to color-matched 252, 252, 252, 0 in order to be
    consistent with Jellyfin's library cover styling.
    :param height_offset: Height offset (in pixels) to make the text off-center. Positive integers will move the text
    upward. Defaults to manually matched 64 in order to be consistent with Jellyfin's library cover styling.
    :return: The image with the text drawn on it.
    """
    # Unpack size into width and height variables
    image_width, image_height = size

    # Compose the message before measuring or drawing it. Titles arrive verbatim from
    # the command line, and no shell normalises them, so a decomposed title (an "e"
    # followed by a combining accent, which is how macOS stores filenames) would
    # otherwise render with the accents dropped and the text pushed off the cover.
    message = unicodedata.normalize("NFC", message)

    # Pin the basic layout engine. Pillow would otherwise pick raqm whenever a system
    # fribidi library happens to be installed, which would make the same title render
    # differently from one machine to the next. Raqm's only effect on the bundled font
    # is kerning, which we want off anyway and which the basic engine never applies.
    font: ImageFont.FreeTypeFont = ImageFont.truetype(
        font_path, font_size, layout_engine=ImageFont.Layout.BASIC
    )

    # Prepare to draw on the image
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

    # Get the height and width of the text message for centering
    _, _, draw_width, draw_height = draw.textbbox((0, 0), message, font=font)

    # Figure out how far below the baseline the text goes
    # "ls" is "left baseline" as our (0,0) anchor
    _, _, _, descender_height = draw.textbbox((0, 0), message, anchor="ls", font=font)

    draw_height -= descender_height

    # Draw the text in the center of the image, accounting for offset
    draw.text(
        (
            (image_width - draw_width) / 2,
            (image_height - height_offset - draw_height) / 2,
        ),
        message,
        font=font,
        fill=font_color,
    )

    return image


def resize_image(
    image: Image.Image,
    width: int = Params.WIDTH.value,
    height: int = Params.HEIGHT.value,
    resample: Image.Resampling = Image.Resampling.BILINEAR,
) -> Image.Image:
    """
    Resizes an image.
    :param image: The image to resize.
    :param width: The width to resize to. Defaults  in order to be consistent with Jellyfin's library cover styling.
    :param height: The height to resize to. Defaults  in order to be consistent with Jellyfin's library cover styling.
    :param resample: The resampling filter to use for resizing. Defaults to bilinear, matching the previous OpenCV
    implementation's interpolation.
    :return: The resized image.
    """
    resized_image: Image.Image = image.resize((width, height), resample=resample)
    return resized_image


def apply_shadow(
    image: Image.Image, shadow: float = Params.FOREGROUND_WEIGHT.value
) -> Image.Image:
    """
    Darkens the image by blending it toward black, producing the shadow overlay effect used by Jellyfin's library cover
    styling.
    :param image: The image to darken.
    :param shadow: The relative weight of the black overlay. 0 leaves the image unchanged, 1 makes it fully black.
    :return: The darkened image.
    """
    shadowed_image: Image.Image = ImageEnhance.Brightness(image).enhance(1.0 - shadow)
    return shadowed_image


def create_library_image(
    file: str,
    library_name: str,
    destination: str = str(),
    shadow: float = Params.FOREGROUND_WEIGHT.value,
    font: Optional[str] = None,
) -> Path:
    """
    The main function for this module. Combines other functions to generate a library image for use in Jellyfin or Emby.
    Outputs to the same directory as the input file.
    :param file: The base image file to use for the Jellyfin library cover. Ideally is 960x540 (1080p) ratio and at
    least that large. The output of this function will write a new file to the directory of this file with " (Cover)"
    appended.
    :param library_name: The text to use for the library image.
    :param destination:
    :param shadow: The foreground weight to use for the library image.
    :param font: Optional path to a font file (.ttf/.otf) to use for the title text. Defaults to the bundled Prima
    Sans Bold, which only covers Latin characters — pass a font with the needed coverage for other scripts.
    :return: The file path of the output image.
    """
    # Read in the image file, normalised to RGB (handles palette, RGBA, and grayscale inputs)
    background: Image.Image = Image.open(file).convert("RGB")

    # Resize the image for Jellyfin
    resized_background: Image.Image = resize_image(background)

    # Darken the image for the shadow overlay effect
    library_cover: Image.Image = apply_shadow(resized_background, shadow)

    # Write the library name onto the shaded image, using the provided font file
    # when given and the bundled Prima Sans Bold otherwise
    font_path = font if font else get_font_path()
    library_cover = write_font_center(
        library_cover, library_cover.size, library_name, font_path
    )

    # String manipulation to determine the file path of the input image and output target.

    if len(destination) == 0:
        path = Path(file)
        file_path: Path = path.parents[0]
        file_name: str = path.stem
        file_extension: str = path.suffix
        output_file_name: str = f"{str(file_path)}/{file_name} (Cover){file_extension}"
    else:
        if os.path.isdir(destination):
            file_name: str = Path(file).stem
            file_extension: str = Path(file).suffix
            output_file_name: str = (
                f"{destination}/{file_name} (Cover){file_extension}"
            )
        else:
            output_file_name: str = destination

    # Write the library cover. JPEG quality matches the previous OpenCV implementation's
    # default (95) rather than Pillow's lower default (75).
    save_options = (
        {"quality": 95}
        if Path(output_file_name).suffix.lower() in (".jpg", ".jpeg")
        else {}
    )
    library_cover.save(output_file_name, **save_options)

    return Path(output_file_name)
