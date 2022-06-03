# image-thumbnail
A Python tool to shrink images to your desire in a multi-process manner.

## Install
```
$ make install
```

## Usage
```
$ ./process.py --help

Usage: process.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  downscale  Shrink images till a max dimension in pixels (width, height).
  downsize   Shrink images till a max size in MB.
```

## Examples

**Shrink image, no more than 3000 x 3000 pixels**
```bash
# Shrink images in /Downloads, output into /Desktop
./process.py downscale /Downloads /Desktop -d 3000
```

**Shrink image, no more than 2 MB**
```bash
# Shrink images in /Downloads, output into /Desktop
./process.py downsize /Downloads /Desktop -s 2
```

## For Developers
```
$ make dep
$ source .env/bin/activate
```
