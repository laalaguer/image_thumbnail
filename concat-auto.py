''''
    Concat all the images automatically under one folder.
'''

import os
from image_thumbnail import utils

def process_files_in_folder(folder_path, direction:bool, remove_after:bool, width_aspect_ratio: int, height_aspect_ratio: int):
    ''' Concat ALL images under one folder.

        direction: True=horizontal, False=vertical
        remove_after: Remove original images after concat.
    '''
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    full_paths = [os.path.join(folder_path, f) for f in files]
    imgs = [file for file in full_paths if (not utils.is_hidden_file(file)) and utils.is_img(file)]

    if len(imgs) < 2:
        return

    imgs = sorted(imgs) # sort path strings by name
    PIL_imgs = [utils.open_img(img) for img in imgs] # Convert to img objects
    big_img = utils.concat_imgs_2(PIL_imgs, direction, width_aspect_ratio, height_aspect_ratio) # Concat into one
    big_img_path = imgs[0] + '.jpg'
    utils.save_jpg(big_img, big_img_path) # Save

    if remove_after:
        for img in imgs:
            utils.silent_remove(img)
            

def recursive(folder_path, direction:bool, remove_after, width_aspect_ratio: int, height_aspect_ratio: int):
    ''' Recursively do the operation '''
    # If sub-folder is found, do the sub folder
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            recursive(subfolder_path, direction, remove_after)
    # Do the grouping
    process_files_in_folder(folder_path, direction, remove_after, width_aspect_ratio, height_aspect_ratio)


if __name__ == "__main__":
    print("Concat images under one folder,\nCan go recursively into-sub folders")

    folder = input('Folder: ')

    direction = input('Concat horizontally? press Enter to skip (y/N): ')
    if direction and direction.lower() == 'n':
        direction = False
    else:
        direction = True

    r = input('Recursive go into sub-folders? (y/N): ')
    if r and r.lower() == 'n':
        r = False
    else:
        r = True
    
    remove = input('Remove original files after concat? (y/N): ')
    if remove and remove.lower() == 'n':
        remove = False
    else:
        remove = True

    width_aspect_ratio = int(input('Width aspect ratio (default 3): ') or 3)
    height_aspect_ratio = int(input('Height aspect ratio (default 2): ') or 2)

    if r:
        recursive(folder, direction, remove, width_aspect_ratio, height_aspect_ratio)
    else:
        process_files_in_folder(folder, direction, remove)