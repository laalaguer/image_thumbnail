# image-thumbnail
A Python tool to shrink images to your desire in a multi-process manner.

### Common Screen resolutions

| Device | Width | Height |
|--------|-------|--------|
|720p | 1280* | 720 |
|1080p | 1920 | 1080| 
|2k | 2560 | 1440 |
|4k | 4096* | 2160 |
|iPhone SE 3| 1344| 750 |
|iPhone 14 Pro| 2556 | 1179 |
|Galaxy S23 | 2340 | 1080 | 

Stock image resolution at **< 1280** is inadequate for morden screens, and **> 4096** can be considered an overkill.

Common size is around **2500**.


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
python3 ./process.py downscale /Downloads /Desktop -d 3000
```

**Shrink image, no more than 2 MB**
```bash
# Shrink images in /Downloads, output into /Desktop
python3 ./process.py downsize /Downloads /Desktop -s 2
```

## For Developers
```
$ make dep
$ source .env/bin/activate
```
