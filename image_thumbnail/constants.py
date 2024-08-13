'''
    JPEG Image Resolutions, Quality and Storage size

    Dimension:

    5000x5000, 95, 3.5MB ~ 6MB, mostly ~5MB
    3500x3500, 95, 1.5MB ~ 3MB, mostly ~2MB

    Quality: 
    
    95/100 = 2.7x size (visually similar)
    90/95  = 2x size (visually downgraded a little)
    85/90  = 0.6 size (acceptable blur)

    [15%, 21%, 36%, 100%]

'''
class Resolutions:
    # Desktop
    MAC_STUDIO_DISPLAY  = max([5120, 2880]) # Best
    MAC_ULTRAFINE_4K    = max([5120, 2880])
    MACBOOK_PRO_2021    = max([3456, 2234]) # Good
    MACBOOK_PRO_2015    = max([2880, 1800]) # OK

    # Tablet
    IPAD_PRO_2021       = max([2732, 2048])
    IPAD_MINI_6         = max([2266, 1488])

    # Mobile
    IPHONE_13_PRO_MAX   = max([2778, 1284])
    IPHONE_13_PRO       = max([2532, 1170])
    IPHONE_8            = max([1334, 750])  # Minimum (Light)

    JPEG_BEST           = MAC_STUDIO_DISPLAY
    JPEG_GOOD           = MACBOOK_PRO_2021
    JPEG_OK             = MACBOOK_PRO_2015
    JPEG_LIGHT          = IPHONE_8


class StorageSizes:
    # in MB
    JPEG_BEST      = 4.5
    JPEG_GOOD      = 1.5
    JPEG_OK        = 1
    JPEG_LIGHT     = 0.5


class ImageQuality:
    # int
    JPEG_LOSSLESS   = 100
    JPEG_BEST       = 95
    JPEG_GOOD       = 90
    JPEG_OK         = 85
    JPEG_LIGHT      = 80


IMAGE_SUFFIX = [
    '.jpeg',
    '.jpg',
    '.png',
    '.gif',
    '.webp',
    '.tiff',
    '.psd',
    '.raw',
    '.bmp',
    '.heif',
    '.heic',
    '.svg'
]
