SRC=$1
DST=$2
TIME=$3
DESC=$4

echo $SRC
echo $DST
echo $TIME
echo $DESC

python3 process.py set-exif \
	-t datetime -t "${TIME}" \
	-t datetime_original -t "${TIME}" \
	-t image_description -t "${DESC}" \
	"${SRC}" "${DST}"
