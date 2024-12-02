''' Interface to image process '''
import click
from pathlib import Path
from image_thumbnail import (
    utils,
    constants
)

@click.group()
def cli():
    pass

@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
@click.option('-s', '--size', type=float, required=False, default=constants.StorageSizes.JPEG_GOOD, prompt="Process files till less than () MB?", help='Process files till less than () MB?')
@click.option('-q', '--quality', type=int, required=False, default=constants.ImageQuality.JPEG_GOOD, prompt="[1-100] JPEG image quality (bigger is better)", help='[1-100] JPEG image quality (bigger is better)')
@click.option('-f', '--force', is_flag=True, show_default=True, default=False, help="Enfore every image converted to JPG")
@click.option('-t', '--tag', type=str, required=False, default=[], multiple=True, prompt="EXIF tag to be removed, eg. image_description, exposure_mode. Can use -t multiple times.", help="EXIF tag to be removed, eg. image_description, exposure_mode. Can use -t multiple times.")
def down_size(src, dst, size, quality, force, tag):
    '''
        Shrink images till a max size in MB.

        Read from SRC folder, store in DST folder. (non-images are simply copied)
    '''
    click.echo(f'src: {src}, dst: {dst}, size: {size} MB, quality: {quality}, force jpg: {force}, tags: {tag}')
    config = {
        'max_size_mb': float(size),
        'quality': quality,
        'force_jpg': force,
        'tags': [x.lower() for x in tag]
    }
    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        constants.IMAGE_SUFFIX,
        'down_size',
        config
    ):
        print(f'\r{message}', end='')
    print()

@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
@click.option('-d', '--dimension', type=int, required=False, default=0, prompt="Max dimension (eg. width, height), if 0 then size unchanged", help='Max dimension (eg. width, height), if 0 then size unchanged')
@click.option('-q', '--quality', type=int, required=False, default=constants.ImageQuality.JPEG_GOOD, prompt="[1-100] JPEG image quality (bigger is better)", help='[1-100] JPEG image quality (bigger is better)')
@click.option('-t', '--tag', type=str, required=False, default=[], multiple=True, prompt="EXIF tag to be removed, eg. image_description, exposure_mode. Can use -t multiple times.", help="EXIF tag to be removed, eg. image_description, exposure_mode. Can use -t multiple times.")
@click.option('-s', '--skipunder', type=float, required=False, default=0, prompt="Skip images under this ?MB, if 0 then no skip", help='Skip images under this ?MB, if 0 then no skip')
def down_scale(src, dst, dimension, quality, tag, skipunder):
    '''
        Shrink images till a max dimension in pixels (width, height).

        Read from SRC folder, store in DST folder. (non-images are simply copied)
    '''
    click.echo(f'src: {src}, dst: {dst}, dimension: {dimension}x{dimension} pixels, quality: {quality}')
    config = {
        'max_dimension': int(dimension),
        'quality': quality,
        'tags': [x.lower() for x in tag],
        'skip_under_mb': float(skipunder)
    }
    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        constants.IMAGE_SUFFIX,
        'down_scale',
        config
    ):
        print(f'\r{message}', end='')
    print()


@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
def remove_black_bar(src, dst):
    '''
        Remove the black bar from images.

        Read from SRC folder, store in DST folder. (non-images are simply copied)
    '''
    click.echo(f'src: {src}, dst: {dst}')
    config = {}
    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        constants.IMAGE_SUFFIX,
        'remove_black_bar',
        config
    ):
        print(f'\r{message}', end='')
    print()


@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
@click.option('-t', '--tag', type=str, required=True, default=[], multiple=True, prompt="EXIF tag to be removed, eg. image_description, exposure_mode. Can use -t multiple times.", help="EXIF tag to be removed, eg. image_description, exposure_mode. Can use -t multiple times.")
def strip_exif(src, dst, tag):
    ''' Strip EXIF tags off images.
    '''
    click.echo(f'src: {src}, dst: {dst}, tag: {tag}')
    config = {
        'tags': [x.lower() for x in tag]
    }
    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        constants.IMAGE_SUFFIX,
        'strip_exif',
        config
    ):
        print(f'\r{message}', end='')
    print()


@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
@click.option('-t', '--tag', type=str, required=True, default=[], multiple=True, prompt="Exif Tags to be writte. Eg. -t artist -t john", help="Exif Tags to be writte. Eg. -t artist -t john")
def set_exif(src, dst, tag):
    ''' Write EXIF tags of images.
    '''
    click.echo(f'src: {src}, dst: {dst}, tag: {tag}')
    if len(tag) % 2 != 0:
        click.echo(f'-t option must be used in even manner')
        return

    if len(tag) == 0:
        click.echo(f'-t option must be specified')
        return

    keys = []
    
    for idx in range(0, len(tag), 2):
        keys.append(tag[idx])
    
    values = []
    for idx in range(1, len(tag), 2):
        values.append(tag[idx])
    
    key_value = zip(keys, values)
    config = {x[0]:x[1] for x in key_value}

    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        constants.IMAGE_SUFFIX,
        'set_exif',
        config
    ):
        print(f'\r{message}', end='')
    print()


cli.add_command(down_size)
cli.add_command(down_scale)
cli.add_command(remove_black_bar)
cli.add_command(strip_exif)
cli.add_command(set_exif)

if __name__ == '__main__':
    cli()
