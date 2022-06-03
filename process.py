''' Interface to image process '''
import click
from pathlib import Path
from image_thumbnail import utils, constants

COMMON_SUFFIXES = ['.png', '.jpeg', '.jpg', '.bmp']

@click.group()
def cli():
    pass

@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
@click.option('-s', '--size', type=float, required=False, default=constants.StorageSizes.JPEG_GOOD, prompt="Process files till less than () MB?", help='Process files till less than () MB?')
@click.option('-q', '--quality', type=int, required=False, default=constants.ImageQuality.JPEG_GOOD, prompt="[1-100] JPEG image quality (bigger is better)", help='[1-100] JPEG image quality (bigger is better)')
def downsize(src, dst, size, quality):
    '''
        Shrink images till a max size in MB.

        Read from SRC folder, store in DST folder. (non-images are simply copied)
    '''
    click.echo(f'src: {src}, dst: {dst}, size: {size} MB, quality: {quality}')
    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        COMMON_SUFFIXES,
        'down_size',
        {'max_size_mb': float(size), 'quality': quality}
    ):
        print(f'\r{message}', end='')
    print()

@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True), required=True)
@click.argument('dst', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True), required=True)
@click.option('-d', '--dimension', type=int, required=False, default=constants.Resolutions.JPEG_GOOD, prompt="Max dimension (eg. width, height)?", help='Max dimension (eg. width, height)?')
@click.option('-q', '--quality', type=int, required=False, default=constants.ImageQuality.JPEG_GOOD, prompt="[1-100] JPEG image quality (bigger is better)", help='[1-100] JPEG image quality (bigger is better)')
def downscale(src, dst, dimension, quality):
    '''
        Shrink images till a max dimension in pixels (width, height).

        Read from SRC folder, store in DST folder. (non-images are simply copied)
    '''
    click.echo(f'src: {src}, dst: {dst}, dimension: {dimension}x{dimension} pixels, quality: {quality}')
    for message in utils.scan_multi(
        Path(src),
        Path(dst),
        COMMON_SUFFIXES,
        'down_scale',
        {'max_dimension': int(dimension), 'quality': quality}
    ):
        print(f'\r{message}', end='')
    print()


cli.add_command(downsize)
cli.add_command(downscale)

if __name__ == '__main__':
    cli()