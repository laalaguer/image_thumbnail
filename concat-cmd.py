'''    
    Concat images into one image.
    Command-line mode, user provides input via flags.
    
    Usage:
        python concat-cmd.py \
        -d horizontal \
        -i image1.jpg image2.jpg image3.jpg \
        -w 3 \
        -t 2 \
        -o output.jpg


'''
import argparse
from image_thumbnail import utils

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Concatenate images into one image.")
    parser.add_argument(
        '-d', '--direction', 
        type=str, 
        choices=['horizontal', 'vertical'], 
        default='horizontal', 
        help="Direction to concatenate images: 'horizontal' or 'vertical' (default: horizontal)."
    )
    parser.add_argument(
        '-i', '--images', 
        nargs='+', 
        required=True, 
        help="List of image file paths to concatenate."
    )
    parser.add_argument(
        '-w', '--width-aspect-ratio', 
        type=int, 
        default=3, 
        help="Width aspect ratio (default: 3)."
    )
    parser.add_argument(
        '-t', '--height-aspect-ratio', 
        type=int, 
        default=2, 
        help="Height aspect ratio (default: 2)."
    )
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        required=True, 
        help="Output file path for the concatenated image."
    )

    # Parse arguments
    args = parser.parse_args()

    # Determine direction
    direction = True if args.direction == 'horizontal' else False

    # Open images
    imgs = [utils.open_img(x) for x in args.images]

    if len(imgs) < 2:
        print("Error: At least two images are required for concatenation.")
        exit(1)

    # Concatenate images
    big_img = utils.concat_imgs_2(imgs, direction, args.width_aspect_ratio, args.height_aspect_ratio)

    # Save the concatenated image
    utils.save_jpg(big_img, args.output)
    print(f"Concatenated image saved to {args.output}")

if __name__ == "__main__":
    main()