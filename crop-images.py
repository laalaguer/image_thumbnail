''' Crop out part of image (like bottom) '''
import os
from PIL import Image
from image_thumbnail import utils

def calculate_crop_box(image_path:str, side:str, percentage:float):
    """
    Calculate the crop box for the specified side and percentage.

    Parameters:
        image (str): The path of a image to be cropped.
        side (str): The side to crop, one of 'top', 'bottom', 'left', 'right'.
        percentage (float): The percentage to crop (0-99.9).

    Returns:
        tuple: A box (left, upper, right, lower) for the crop method.
    """
    image = Image.open(image_path)
    width, height = image.size
    image.close()
    crop_amount = int((percentage / 100) * width if side in ['left', 'right'] else (percentage / 100) * height)

    if side == 'left':
        box = (crop_amount, 0, width, height)
    elif side == 'right':
        box = (0, 0, width - crop_amount, height)
    elif side == 'top':
        box = (0, crop_amount, width, height)
    elif side == 'bottom':
        box = (0, 0, width, height - crop_amount)
    else:
        raise ValueError("Side must be one of 'top', 'bottom', 'left', 'right'.")

    return box


def crop_image(input_path, output_path, box):
    ''' Crop image according to a box '''
    image = Image.open(input_path)
    cropped_image = image.crop(box)
    cropped_image.save(output_path)


def crop_images_in_folder(source_folder, destination_folder, cut_percent:float, cut_side:str):
    ''' Recursive '''
    for root, _, files in os.walk(source_folder):
        files.sort()
        for filename in files:
            if utils.is_img(filename):
                relative_path = os.path.relpath(root, source_folder)
                input_path = os.path.join(root, filename)
                output_dir = os.path.join(destination_folder, relative_path)
                output_path = os.path.join(output_dir, filename)

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                _box = calculate_crop_box(input_path, cut_side, cut_percent)
                crop_image(input_path, output_path, _box)


if __name__ == "__main__":

    source_folder = input("SRC folder: ")
    destination_folder = input("DST folder: ")

    cut_side = input("Side to cut, eg. left, right, top, bottom: ")
    cut_side = cut_side.strip()

    percent_to_cut = input("Percent to cut, eg. 15.1 (= 15.1%): ")
    percent_to_cut = float(percent_to_cut.strip())

    crop_images_in_folder(source_folder, destination_folder, percent_to_cut, cut_side)
