import io
import shutil
from pathlib import Path
import multiprocessing
from multiprocessing import Pool
from typing import List, Callable, Union

import PIL
from PIL import (
    Image as PILImage,
    ExifTags
)

from exif import (
    Image as EXIFImage
)

from .constants import (
    StorageSizes,
    ImageQuality
)

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
    # Set up configurations, if not configured then use "middle" range options
    quality = config.get('quality', ImageQuality.JPEG_GOOD)
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
            output_pic_file_name = Path(output_stem).with_suffix(original_pic.suffix)
            output_pic_path = output_folder.joinpath(output_pic_file_name)
            just_copy_file(original_pic, output_pic_path)
        else:
            # Output file final path
            output_pic_file_name = Path(output_stem).with_suffix('.jpg')
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
    # output file final path
    output_pic_file_name = Path(output_stem).with_suffix('.jpg')
    output_pic_path = output_folder.joinpath(output_pic_file_name)

    # Set up configurations, if not configured then use "middle" range options
    max_dimension = config.get('max_dimension', 0)
    quality = config.get('quality', ImageQuality.JPEG_GOOD) # 95% quality can save 1/2 space
    tags = config.get('tags', [])

    try:
        im = PILImage.open(original_pic)
        if im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        if max_dimension == 0:
            max_dimension = max(im.size)

        im.thumbnail((max_dimension, max_dimension), resample=PIL.Image.Resampling.LANCZOS)
        my_exif = im.getexif()
        my_exif = _strip_exif_tags(my_exif, tags)

        im.save(output_pic_path, "JPEG", quality=quality, exif=my_exif)
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
    # output file final path
    output_pic_file_name = Path(output_stem).with_suffix(original_pic.suffix)
    output_pic_path = output_folder.joinpath(output_pic_file_name)

    tags = config.get('tags', [])

    try:
        _strip_exif_tags_2(original_pic, output_pic_path, tags)
    except Exception as e:
        print(e)


class ImageHelper:
    registry = {
        'down_size': down_size,
        'down_scale': down_scale,
        'strip_exif': strip_exif
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