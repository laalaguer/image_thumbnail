''''
    Concat images into one image.
    Manual mode, user shall select images to concat.
'''
from image_thumbnail import utils

def get_user_inputs(hint='set a hint: '):
    ''' Hint user to provide input, pure "enter" will end the input '''
    user_inputs = []
    while True:
        user_input = input(hint)
        if not user_input:
            break
        user_inputs.append(user_input.strip())
    return user_inputs

if __name__ == "__main__":
    print('Concat images')

    direction = input('Concat horizontally? press Enter to skip (y/N): ')
    if direction and direction.lower() == 'n':
        direction = False
    else:
        direction = True

    images = get_user_inputs('Enter image file full path, press Enter to stop: ')
    imgs = [utils.open_img(x) for x in images]

    if len(imgs) < 2:
        exit()
    
    width_aspect_ratio = int(input('Width aspect ratio (default 3): ') or 3)
    height_aspect_ratio = int(input('Height aspect ratio (default 2): ') or 2)

    big_img = utils.concat_imgs_2(imgs, direction, width_aspect_ratio, height_aspect_ratio)

    big_img_path = images[0] + '.jpg'

    utils.save_jpg(big_img, big_img_path)