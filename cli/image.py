# Standard library imports
import os
from pathlib import Path
from typing import List, Tuple

# Package imports
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image


def get_font_path(
    font_file: str = "Prima Sans Bold.otf",
    font_dir: str = "fonts",
    path_to_fonts: str = Path(__file__).parent,
) -> str:
    """
    Gets a path of a given font file within this package.
    :param font_file: The name of the font file to get the path for. Defaults to the Jellyfin library cover font (Prima
    Sans Bold).
    :param font_dir: The parent directory containing the `font_file`. Defaults to the `fonts` folder in this package.
    :param path_to_fonts: The top-level absolute path to `font_dir`. Defaults to the parent directory of this package.
    :return: Absolute path of the font file.
    """
    font_path: str = os.path.join(path_to_fonts, font_dir, font_file)
    return font_path


def write_font_center(
    image: np.ndarray,
    size: Tuple[int, int],
    message: str,
    font_path: str = get_font_path(),
    font_size: int = 112,
    text_color: Tuple[int, int, int, int] = (252, 252, 252, 0),
    features: List[str] = ["-kern"],
    height_offset: int = 64,
) -> np.core.multiarray:
    """
    Function for writing text in a given font on an image.
    :param image: The image on which to draw text.
    :param size: The width and height (in pixels) of the `image`.
    :param message: The text to write on the image.
    :param font_path: The absolute path to the font to use on the image.
    :param font_size: The size of the font to use. Defaults to manually matched 112 in order to be consistent with
    Jellyfin's library cover styling.
    :param text_color: The RGBA color of the font to use. Defaults to color-matched 252, 252, 252, 0 in order to be
    consistent with Jellyfin's library cover styling.
    :param features: Pillow features to use while drawing the font. Defaults to remove kerning in order to be consistent
    with Jellyfin's library cover styling.
    :param height_offset: Height offset (in pixels) to make the text off-center. Positive integers will move the text
    upward. Defaults to manually matched 64 in order to be consistent with Jellyfin's library cover styling.
    :return: NumPy array reporesenting the new image with drawn text.
    """
    # Unpack size into width and height variables
    image_width, image_height = size

    # Define the font as a variable
    font: ImageFont.FreeTypeFont = ImageFont.truetype(font_path, font_size)

    # Turn the image into a pillow ImageDraw
    pillow_image: Image = Image.fromarray(image)
    draw: ImageDraw = ImageDraw.Draw(pillow_image)

    # Get the height and width of the text message for centering
    _, _, draw_width, draw_height = draw.textbbox(
        (0, 0), message, font=font, features=features
    )

    # Draw the text in the center of the image, accounting for offset
    draw.text(
        (
            (image_width - draw_width) / 2,
            (image_height - height_offset - draw_height) / 2,
        ),
        message,
        font=font,
        fill=text_color,
        features=features,
    )

    # Convert the image into a numpy array
    image: np.core.multiarray = np.array(pillow_image)
    return image


def resize_image(
    image: np.ndarray,
    width: int = 960,
    height: int = 540,
    interpolation: int = cv2.INTER_LINEAR,
) -> np.ndarray:
    """

    :param image: The image to resize.
    :param width: The width to resize to. Defaults  in order to be consistent with Jellyfin's library cover styling.
    :param height: The height to resize to. Defaults  in order to be consistent with Jellyfin's library cover styling.
    :param interpolation: Integer representation of the interpolation method to use for resizing.
    :return: The resized image as a NumPy `ndarray`.
    """
    resized_image: np.ndarray = cv2.resize(
        image, (width, height), interpolation=interpolation
    )
    return resized_image


def generate_black_layer(
    height: int, width: int, channels: int, dtype: str = "uint8"
) -> np.ndarray:
    """
    Generates a layer of black to overlay on the base image used for the library cover.
    :param height: Height of layer to generate.
    :param width: Width of the layer to generate.
    :param channels: Number of channels in the layer to generate.
    :param dtype: String-represented desired data-type for the array.
    :return: The black layer image as a NumPy ndarray.
    """
    layer: np.ndarray = np.zeros((height, width, channels), dtype=dtype)
    return layer


def overlay_images(
    foreground: np.ndarray,
    background: np.ndarray,
    foreground_weight: float = 0.5,
    background_weight: float = 0.5,
) -> np.ndarray:
    """
    Overlays 2 images with a given transparency.
    :param foreground: The foreground image to overlay.
    :param background: Teh background image to overlay.
    :param foreground_weight: The relative weight of the foreground image to use during the blend. This and
    `background_weight` must add up to 1.
    :param background_weight: The relative weight of the background image to use during the blend. This and
    `foreground_weight` must add up to 1.
    :return: The overlaid image as a NumPy `ndarray`.
    """
    image: np.ndarray = cv2.addWeighted(
        background, background_weight, foreground, foreground_weight, 1.0
    )
    return image


def create_library_image(file: str, library_name: str):
    """
    The main function for this module. Combines other functions to generate a library image for use in Jellyfin or Emby.
    Outputs to the same directory as the input file.
    :param file: The base image file to use for the Jellyfin library cover. Ideally is 960x540 (1080p) ratio and at
    least that large. The output of this function will write a new file to the directory of this file with " (Cover)"
    appended.
    :param library_name: The text to use for the library image.
    """
    # Read in the image file as a cv2 image.
    background: np.ndarray = cv2.imread(file)

    # Resize the image for Jellyfin
    resized_background: np.ndarray = resize_image(background)

    # Get the size of the image in order to create a same-size black overlay layer
    background_size: Tuple[int, int, int] = resized_background.shape

    # Generate a black layer of same size as image for shading overlay
    foreground: np.ndarray = generate_black_layer(*background_size)

    # Overlay the base image and the black overlay for shading effect
    library_cover: np.ndarray = overlay_images(foreground, resized_background)

    # Write the library name onto the shaded image
    height, width = (background_size[0], background_size[1])
    library_cover: np.ndarray = write_font_center(
        library_cover, (width, height), library_name
    )

    # String manipulation to determine the file path of the input image and output target.
    file_path: str = file.rsplit(".", 1)[0]
    file_extension: str = file.rsplit(".", 1)[1]
    output_file_name: str = file_path + " (Cover)." + file_extension

    # Write the library cover in the same directory as the input file.
    cv2.imwrite(output_file_name, library_cover)

    def main():
        pass

    if __name__ == "__main__":
        main()
