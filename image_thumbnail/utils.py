import io
import os
import shutil
from pathlib import Path
import multiprocessing
from multiprocessing import Pool
from typing import List, Callable, Union, Tuple

import PIL
from PIL import (
    Image as PILImage,
    ImageFile as PILImageFile,
    ExifTags
)

from exif import (
    Image as EXIFImage
)

from .constants import (
    StorageSizes,
    JpegImageQuality,
    IMAGE_SUFFIX
)

def is_hidden_file(file_path: Union[str, Path]):
    ''' If is hidden file '''
    file_path = Path(file_path)
    return file_path.name.startswith('.')

def is_img(file_path: str):
    ''' If is supported image '''
    supported = IMAGE_SUFFIX
    for each in supported:
        if file_path.lower().endswith(each.lower()):
            return True
    
    return False

# Load partial images without error
PILImageFile.LOAD_TRUNCATED_IMAGES = True

def if_exists_then_raise(path: Union[str, Path]):
    ''' If path exists then raise exception '''
    path = Path(path)
    if path.exists():
        raise Exception(f'File exists: {path}')

def silent_remove(path: Union[str, Path]):
    ''' Silently remove a file on the os '''
    path = Path(path)
    if path.exists():
        path.unlink()

def _disallow_multi_dot(filename_path: Union[str, Path]):
    '''
        If filepath contains more than 1 dot (the suffix dot)
        raise Exception
    '''
    _value = str(filename_path)
    file_name = os.path.basename(_value)
    counter = 0
    for item in file_name:
        if item == ".":
            counter += 1
    
    if counter > 1:
        raise Exception(f"Contain more than 1 dot in base file name {_value}")

def save_jpg(img:PILImage.Image, output_pic_path:str, quality=85):
    ''' Save an image with to jpg '''
    img.save(output_pic_path, "JPEG", quality=quality)


def open_img(pic_path:str):
    ''' Open an image with correct orientaion '''
    im = PILImage.open(pic_path)
    try:
        exif = im.getexif()
        if exif is not None:
            # Iterate through the EXIF data
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) == 'Orientation':
                    orientation = value
                    break
            else:
                orientation = 1  # Default orientation
        else:
            orientation = 1  # Default orientation
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
        orientation = 1  # Default orientation if there's an error

    # Apply the orientation
    if orientation == 1:
        pass  # No rotation needed
    elif orientation == 3:
        im = im.rotate(180, expand=True)
    elif orientation == 6:
        im = im.rotate(270, expand=True)
    elif orientation == 8:
        im = im.rotate(90, expand=True)

    return im

      
def resize_to_fit(img: PILImage.Image, x, y):
    ''' Size down the img to width x and height y
        Return type Image
    '''
    # Open the original image
    original_image = img
    a, b = original_image.size  # Original dimensions

    # Calculate the aspect ratio
    aspect_ratio = a / b
    target_aspect_ratio = x / y

    if aspect_ratio > target_aspect_ratio:
        # Original image is wider than the target aspect ratio
        new_height = y
        new_width = int(y * aspect_ratio)
    else:
        # Original image is taller than the target aspect ratio
        new_width = x
        new_height = int(x / aspect_ratio)

    # Resize the original image
    resized_image = original_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)

    # Create a new blank image with the target dimensions
    new_image = PILImage.new("RGB", (x, y), (255, 255, 255))  # White background

    # Calculate the position to paste the resized image
    paste_x = (x - new_width) // 2
    paste_y = (y - new_height) // 2

    # Paste the resized image onto the blank image
    new_image.paste(resized_image, (paste_x, paste_y))

    return new_image


def min_size(imgs: List[PILImage.Image]) -> Tuple[int, int]:
    ''' Return the min [width, height] of a list of images '''
    sizes = [x.size for x in imgs]
    widths = [x[0] for x in sizes]
    heights = [x[1] for x in sizes]
    
    min_width = min(widths)
    min_height = min(heights)

    return (min_width, min_height)


def concat_imgs(imgs: List[PILImage.Image], horizontal:bool) -> PILImage.Image:
    ''' Concat images into a horizontal or vertical way

    Args:
        imgs (list): a list of image files
        horizontal (bool): true then make it horizontal, false then vertical

    Returns:
        PIL.Image.Image
    '''
    min_width, min_height = min_size(imgs)
    new_imgs = [resize_to_fit(x, min_width, min_height) for x in imgs]

    if horizontal:
        total_width = min_width * len(new_imgs)
        # Create a new canvas
        concatenated_image = PILImage.new('RGB', (total_width, min_height))
        # Paste images one by one
        current_x = 0
        for image in new_imgs:
            concatenated_image.paste(image, (current_x, 0))
            current_x += min_width
    else:
        total_height = min_height * len(new_imgs)
        # Create a new canvas
        concatenated_image = PILImage.new('RGB', (min_width, total_height))
        # Paste images one by one
        current_y = 0
        for image in new_imgs:
            concatenated_image.paste(image, (0, current_y))
            current_y += min_height
    
    return concatenated_image


def distort(image, width_aspect_ratio: int, height_aspect_ratio: int):
    ''' 
    Distort the aspect ratio of an image.

    If input is a 100x100 image and width_ratio=2, height_ratio=1,
    then the output is of ratio 2:1. So the output is 100x50

    This operation is not expanding: the output width is not longer than input width,
    the output height is no longer than input height.
    
    Parameters:
        image (PIL.Image): The image to be distorted.
        width_aspect_ratio (int): The ratio to distort the width.
        height_aspect_ratio (int): The ratio to distort the height.

    Returns:
        PIL.Image: The distorted image.
    '''
    # Get the original dimensions of the image
    original_width, original_height = image.size

    # Suppose width is not changed.
    new_height = int((original_width / width_aspect_ratio) * height_aspect_ratio)

    # Resize the image to the new dimensions
    distorted_image = image.resize((original_width, new_height), PILImage.Resampling.LANCZOS)

    return distorted_image


def max_process_count(MIN:int=2):
    ''' Compute max processes allowed on this computer '''
    try:
        x = multiprocessing.cpu_count()
        return max([int(x / 2), MIN])
    except:
        return MIN


def just_copy_file(src: Path, dst: Path):
    ''' Copy file from src to dst '''
    shutil.copyfile(src, dst)


def _find_tag_number_by_name(name: str) -> Union[int, None]:
    '''Pillow internal: Find a EXIF tag number, given a string name reference

    Args:
        name (str): EXIF tag name, eg. image_description or ImageDescription

    Returns:
        Union[int, None]: The EXIF number or None if not found.
    '''
    search_name = name.replace('_', '').lower()
    for int_key in ExifTags.TAGS:
        if ExifTags.TAGS[int_key].lower() == search_name:
            return int_key
    return None


def _strip_exif_tags(my_exif: dict, tags: List[str]):
    '''Pillow internal: Strip EXIF tag by name, return modified EXIF dict

    Args:
        exif_info (dict): _description_
        tags (List[str]): _description_
    '''
    int_keys = [_find_tag_number_by_name(x) for x in tags]
    int_keys = [x for x in int_keys if x != None] # filter out None values

    new_exif = my_exif

    for key in new_exif:
        if key in int_keys:
            del new_exif[key]
    
    return new_exif


def _strip_exif_tags_2(src: Path, dst: Path, tags: List[str]):
    '''Strip EXIF tags from a image file, without re-compressing the original file.

    Args:
        src (Path): source image
        dst (Path): output image
        tags (str]): eg: image_description, xp_comment.
    '''
    my_image = None
    with open(src, 'rb') as in_file:
        my_image = EXIFImage(in_file)

    if my_image.has_exif:
        for k in my_image.list_all():
            if k in tags:
                del my_image[k]

    with open(dst, 'wb') as out_file:
        out_file.write(my_image.get_file())


def compute_relative_path(longer: Path, shorter: Path) -> Union[Path, None]:
    ''' 
        Compute the chunk of relative path between shorter one and longer one.
        Can raise value error if shorter isn't part of longer.
    '''
    return shorter.relative_to(longer)


def down_size(original_pic: Path, output_stem: str, output_folder: Path, config:dict):
    ''' Downsize an image, up till desired size, into JPEG format

        Parameters
        ----------
        config: {'max_size_mb':float, 'quality':int, 'force_jpg':bool, 'tags':List[str]}
    '''
    # _disallow_multi_dot(original_pic)

    # Set up configurations, if not configured then use "middle" range options
    quality = config.get('quality', JpegImageQuality.JPEG_GOOD)
    max_size_mb = config.get('max_size_mb', StorageSizes.JPEG_GOOD)
    force_jpg = config.get('force_jpg', False)
    tags = config.get('tags', [])
    
    flag_file_is_jpg = original_pic.suffix.lower() == '.jpg' or original_pic.suffix.lower() == '.jpeg'
    flag_file_size_exceeded = original_pic.stat().st_size > max_size_mb * 1024 * 1024

    try:
        im = PILImage.open(original_pic)
        my_exif = im.getexif()
        my_exif = _strip_exif_tags(my_exif, tags)

        if im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        flag_should_transform = False

        if flag_file_size_exceeded:
            flag_should_transform = True
        if not flag_file_is_jpg:
            if force_jpg:
                flag_should_transform = True

        
        if not flag_should_transform:
            # Output file final path
            output_pic_file_name = Path(output_stem + original_pic.suffix)
            output_pic_path = output_folder.joinpath(output_pic_file_name)
            if_exists_then_raise(output_pic_path)
            just_copy_file(original_pic, output_pic_path)
        else:
            # Output file final path
            output_pic_file_name = Path(output_stem + '.jpg')
            output_pic_path = output_folder.joinpath(output_pic_file_name)

            longer_side = max([im.width, im.height])
            
            # To achieve fast tryouts, do 1/2 dimension for once first
            semi_side = int(longer_side / 2)
            im_copy = im.copy()
            im_copy.thumbnail((semi_side, semi_side), resample=PIL.Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            im_copy.save(buffer, "JPEG", quality=quality, exif=my_exif)
            
            # If semi size is still too big
            if len(buffer.getvalue()) > max_size_mb * 1024 * 1024:
                longer_side = semi_side
                # print(f'{original_pic} Too big, start from half dimension {semi_side}')
            else:
                pass

            factor = 0.9 # Shrink factor
            counter = 1  # Round of process
            while True:
                im_copy = im.copy()
                new_width = int(longer_side * (factor ** counter))
                new_height = int(longer_side * (factor ** counter))
                counter += 1
                
                # Try to do the thumbnail
                im_copy.thumbnail((new_width, new_height), resample=PIL.Image.Resampling.LANCZOS)

                # Save thumbnail to memory and check if size exceeds the limit
                # If not, save it to a disk
                buffer = io.BytesIO()
                im_copy.save(buffer, "JPEG", quality=quality)
                if len(buffer.getvalue()) > max_size_mb * 1024 * 1024:
                    continue
                else:
                    if_exists_then_raise(output_pic_path)
                    im_copy.save(output_pic_path, "JPEG", quality=quality, exif=my_exif)
                    print("save:", output_pic_path)
                    break

    except Exception as e:
        print(e)


def down_scale(original_pic: Path, output_stem: str, output_folder: Path, config:dict):
    '''
        Downscale an image into JPEG format

        Parameters
        ----------
        config: {'max_dimension':int, 'quality':int, 'tags':List[str]}
    '''
    # _disallow_multi_dot(original_pic)
    # output file final path
    output_pic_file_name = Path(output_stem+'.jpg')
    output_pic_path = output_folder.joinpath(output_pic_file_name)

    # Set up configurations, if not configured then use "middle" range options
    max_dimension = config.get('max_dimension', 0)
    quality = config.get('quality', JpegImageQuality.JPEG_GOOD) # 95% quality can save 1/2 space
    tags = config.get('tags', [])

    skip_under_mb = config.get('skip_under_mb', 0)
    
    shall_skip_flag = False
    if skip_under_mb == 0:
        shall_skip_flag = True
    else:
        if original_pic.stat().st_size < skip_under_mb * 1024 * 1024:
            shall_skip_flag = True
    
    if shall_skip_flag:
        # remain the original file suffix if the file is to be copied.
        output_pic_file_name = Path(output_stem + original_pic.suffix)
        output_pic_path = output_folder.joinpath(output_pic_file_name)
        just_copy_file(original_pic, output_pic_path)
        return

    try:
        im = PILImage.open(original_pic)
        if im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        if max_dimension == 0:
            max_dimension = max(im.size)

        im.thumbnail((max_dimension, max_dimension), resample=PIL.Image.Resampling.LANCZOS)
        my_exif = im.getexif()
        my_exif = _strip_exif_tags(my_exif, tags)

        if_exists_then_raise(output_pic_path)
        im.save(output_pic_path, "JPEG", quality=quality, exif=my_exif)
        print("save:", output_pic_path)
    except Exception as e:
        print(e)


def distort_images(original_pic: Path, output_stem: str, output_folder: Path, config:dict):
    output_pic_file_name = Path(output_stem + '.jpg')
    output_pic_path = output_folder.joinpath(output_pic_file_name)
    
    quality = config.get('quality', JpegImageQuality.JPEG_GOOD)
    width_aspect_ratio = config.get('width_aspect_ratio', -1)
    height_aspect_ratio = config.get('height_aspect_ratio', -1)

    if width_aspect_ratio <= 0 or height_aspect_ratio <= 0:
        raise Exception(f'Width {width_aspect_ratio} and height {height_aspect_ratio} aspect ratio must be positive')
    
    try:
        im = PILImage.open(original_pic)
        if im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        # Distort the image
        im = distort(im, width_aspect_ratio, height_aspect_ratio)

        # Save the distorted image
        if_exists_then_raise(output_pic_path)
        im.save(output_pic_path, "JPEG", quality=quality)
        print("save:", output_pic_path)
    except Exception as e:
        print(e)


def remove_black_bar(original_pic: Path, output_stem: str, output_folder: Path, config:dict):
    ''' Remove black bar from picture '''
    # _disallow_multi_dot(original_pic)
    # output file final path
    output_pic_file_name = Path(output_stem + '.jpg')
    output_pic_path = output_folder.joinpath(output_pic_file_name)

    # Set up configurations, if not configured then use "middle" range options
    quality = JpegImageQuality.JPEG_GOOD # 95% quality can save 1/2 space

    try:
        im = open_img(original_pic)
        if im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        grayscale_image = im.convert("L")
    
        # Find the bounding box of non-black areas
        bbox = grayscale_image.getbbox()

        # Crop the original image
        cropped_image = im.crop(bbox)

        # Save the cropped image
        if_exists_then_raise(output_pic_path)
        cropped_image.save(output_pic_path, "JPEG", quality=quality)
        print("save:", output_pic_path)
    except Exception as e:
        print(e)


def strip_exif(original_pic: Path, output_stem: str, output_folder: Path, config:dict):
    '''Strip EXIF without re-compressing.

    Args:
        original_pic (Path): original pic path
        output_stem (str): output pic stem
        output_folder (Path): output folder
        config (dict): {'tags': [str]}
    '''
    # _disallow_multi_dot(original_pic)
    # output file final path
    output_pic_file_name = Path(output_stem + original_pic.suffix)
    output_pic_path = output_folder.joinpath(output_pic_file_name)

    tags = config.get('tags', [])

    try:
        if_exists_then_raise(output_pic_path)
        _strip_exif_tags_2(original_pic, output_pic_path, tags)
    except Exception as e:
        print(e)


def _remove_exif(src: Path):
    ''' Total removal of EXIF from image '''
    image = PILImage.open(src)
    data = list(image.getdata())
    image2 = PILImage.new(image.mode, image.size)
    image2.putdata(data)
    image2.save(src)


def _open_as_exif_image(src: Path):
    ''' Open as EXIF image.
        raise Exception if cannot read from file.
    '''
    my_image = None
    with open(src, 'rb') as in_file:
        my_image = EXIFImage(in_file)
        return my_image


def open_as_exif_image(src: Path):
    ''' Open as EXIF image, will try to fix corrupted EXIF for once. 
        If can't fix, then raise exception.
    '''
    my_image = None
    try:
        my_image = _open_as_exif_image(src)
    except Exception as e:
        print(f'Error open as EXIF: {src}, retry...')
        # Remove the corrupted EXIF info
        _remove_exif(src)
        # Try re-open, still error then abort with exception
        my_image = _open_as_exif_image

    return my_image


def _set_exifs(my_image: EXIFImage, config: dict) -> Union[EXIFImage, None]:
    try:
        for key in config:
            my_image[key] = config[key]
        return my_image
    except Exception as e:
        print(f'Error set key: {key}')
        return None


def set_exifs(src: Path, my_image: EXIFImage, config: dict) -> EXIFImage:
    ''' Set exif of image, if error occurs try to fix it '''
    max_try = 10
    new_image = None
    while max_try > 0:
        max_try -= 1
        new_image = _set_exifs(my_image, config)
        if new_image:
            break
        else:
            print(f'Error on file: {src}, retry...')
            _remove_exif(src)
            my_image = open_as_exif_image(src)
    
    if new_image is None:
        raise Exception('Cannot set EXIF after max_try exhausted')
    else:
        return new_image


def _set_exif_tags_2(src: Path, dst: Path, config: dict):
    '''Set EXIF tags to its values

    Args:
        src (Path): original pic
        dst (Path): destination pic
        config (dict): {'exif_key', 'value' }
    '''
    my_image = open_as_exif_image(src)    
    my_image = set_exifs(src, my_image, config)
    try:
        with open(dst, 'wb') as out_file:
            out_file.write(my_image.get_file())
    except Exception as e:
        print('Error save:', dst)
        print(e)


def set_exif(original_pic: Path, output_stem: str, output_folder: Path, config:dict):
    ''' config: {'exif_key': 'value' } '''
    # _disallow_multi_dot(original_pic)
    output_pic_file_name = Path(output_stem + original_pic.suffix)
    output_pic_path = output_folder.joinpath(output_pic_file_name)

    try:
        if_exists_then_raise(output_pic_path)
        _set_exif_tags_2(original_pic, output_pic_path, config)
    except Exception as e:
        print(f'set_exif error: {original_pic}')
        print(e)
        raise (e)


class ImageHelper:
    registry = {
        'down_size': down_size,
        'down_scale': down_scale,
        'remove_black_bar': remove_black_bar,
        'strip_exif': strip_exif,
        'set_exif': set_exif,
        'distort_images': distort_images
    }

    @classmethod
    def select_helper(cls, name:str) -> Callable:
        func = cls.registry.get(name, None)
        if func == None:
            raise Exception(f'{name} function not found')
        return func


def scan(src: Path, dst_parent: Path, transform:List[str], method_name:str, config: dict):
    '''
    Scan from root, get all dirs and files.

    Args:
        src (Path): a folder (contain images) as starting point.
        dst_parent (Path): a parent folder where the cloned (downscaled) src folder is put in.
        transform: a list of suffixes, eg. '.png', '.jpeg', '.jpg'
        method_name: one of the image helper method supported
        config: the config that the method needed

    Raises:
        Exception: If scanning path is not file nor dir.
    '''
    # src folder
    src = src.resolve()
    # parent of src folder
    src_parent = src.parent
    # parent of dst folder
    dst_parent = dst_parent.resolve()

    # Set up a registry for all unresolved (un-visited) paths
    unresolved = []
    unresolved.append(src)

    while len(unresolved):
        current = unresolved.pop(0)
        # Directory? Create a same folder in dst, then go deeper.
        if current.is_dir():
            # Exception: path can't be related
            rel_path = compute_relative_path(src_parent, current)            
            new_path = dst_parent.joinpath(rel_path)
            # Exception: cannot create dir
            new_path.mkdir()
            yield f'Create: {new_path}'
            
            # Exception: If encounter "permission" error (can't list)
            for x in current.iterdir():
                unresolved.append(x)

        # File? Copy or transform it.
        elif current.is_file():
            # Exception: path can't be related
            rel_path = compute_relative_path(src_parent, current)
            new_path = dst_parent.joinpath(rel_path)
            
            # Copy or transform?
            if str(new_path.suffix).lower() in transform:
                h = ImageHelper.select_helper(method_name)
                h(current, new_path.stem, new_path.parent, config)
                yield f'Process:{method_name}: {new_path}'
            else:
                just_copy_file(current, new_path)
                yield f'Copy: {new_path}'

        else:
            raise Exception(f'not file, not dir. {current}')


def scan_multi(src: Path, dst_parent: Path, transform:List[str], method_name:str, config: dict):
    '''
    [Multi-process version] Scan from root, get all dirs and files.

    Args:
        src (Path): a folder (contain images) as starting point.
        dst_parent (Path): a parent folder where the cloned (downscaled) src folder is put in.
        transform: a list of suffixes, eg. '.png', '.jpeg', '.jpg'
        method_name: one of the image helper method supported
        config: the config that the method needed

    Raises:
        Exception: If scanning path is not file nor dir.
    '''
    # Multi-process setup
    n_of_cores = max_process_count()
    print(f'multi-workers: {n_of_cores}')

    # src folder
    src = src.resolve()
    # parent of src folder
    src_parent = src.parent
    # parent of dst folder
    dst_parent = dst_parent.resolve()

    # Set up a registry for all unresolved (un-visited) paths
    unresolved = []
    unresolved.append(src)

    downsize_args = []
    while len(unresolved):
        current = unresolved.pop(0)
        # Directory? Create a same folder in dst, then go deeper.
        if current.is_dir():
            # Exception: path can't be related
            rel_path = compute_relative_path(src_parent, current)            
            new_path = dst_parent.joinpath(rel_path)
            # Exception: cannot create dir
            new_path.mkdir()
            yield f'Create: {new_path}'
            
            # Exception: If encounter "permission" error (can't list)
            for x in current.iterdir():
                unresolved.append(x)

        # File? Copy or transform it.
        elif current.is_file():
            # Exception: path can't be related
            rel_path = compute_relative_path(src_parent, current)
            new_path = dst_parent.joinpath(rel_path)

            # Copy or transform?
            if str(new_path.suffix).lower() in transform:
                downsize_args.append(
                    (current, new_path.stem, new_path.parent, config)
                )
                yield f'Process:{method_name}: {new_path}'
            else:
                just_copy_file(current, new_path)
                yield f'Copy: {new_path}'

        else:
            raise Exception(f'not file, not dir. {current}')
    
    # Finally, do the downsize
    with Pool(n_of_cores) as pool:
        h = ImageHelper.select_helper(method_name)
        pool.starmap(h, downsize_args)