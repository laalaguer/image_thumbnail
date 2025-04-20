'''
    Concat images into one image.
    Command-line mode, user provides input via flags.
    
    Usage:
        python concat-json.py \
        -d horizontal \
        --json-file /path/to/instructions.json \
        -w 3 \
        -t 2 \
        --skip-exist
'''
import os
import json
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
        '-j', '--json-file', 
        type=str, 
        required=True, 
        help="Path to the input JSON file for instructions."
    )
    parser.add_argument(
        '-w', '--width-aspect-ratio', 
        type=int, 
        default=9, 
        help="Width aspect ratio (default: 9)."
    )
    parser.add_argument(
        '-t', '--height-aspect-ratio', 
        type=int, 
        default=16, 
        help="Height aspect ratio (default: 16)."
    )
    parser.add_argument(
        '-s', '--skip-exist', 
        action='store_true', 
        help="Skip saving the output image if it already exists."
    )
    parser.add_argument(
        '-v', '--only-vertical', 
        action='store_true', 
        help="If set, only process images that are vertical (taller than wider) do the concatenation."
    )

    # Parse arguments
    args = parser.parse_args()

    # Determine direction
    direction = True if args.direction == 'horizontal' else False

    # Open images
    with open(args.json_file, 'r') as f:
        json_data = json.load(f)


    for video_path, image_paths in json_data.items():
        try:
            # Open images
            imgs = [utils.open_img(img_path) for img_path in image_paths]

            if len(imgs) < 2:
                print(f"Skipping {video_path}: At least two images are required for concatenation.")
                continue
            
            # Find the image width and height
            # decide if the image is vertical or horizontal
            # and if the --only-vertical flag is set
            _width = imgs[0].size[0]
            _height = imgs[0].size[1]
            if _width > _height and args.only_vertical:
                print(f"Skipping concat imgs of {video_path}: Image is wider than taller and --only-vertical is set.")
                continue

            # Concatenate images
            big_img = utils.concat_imgs_2(
                imgs,
                direction,
                width_aspect_ratio=args.width_aspect_ratio,
                height_aspect_ratio=args.height_aspect_ratio
            )

            # Determine output path
            output_stem = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(os.path.dirname(video_path), f"{output_stem}.jpg")
        
            # Check if --skip-exist is set and the output file already exists
            if args.skip_exist and os.path.exists(output_path):
                print(f"Skipping {video_path}: Output file {output_path} already exists.")
                continue
            
            # Remove existing cover.jpg if it exists
            if os.path.exists(output_path):
                os.remove(output_path)

            # Save the concatenated image
            utils.save_jpg(big_img, output_path)
            print(f"Concatenated image saved to {output_path}")
        except Exception as e:
            print(f"Error processing {video_path}: {e}")
            continue
        

if __name__ == "__main__":
    main()