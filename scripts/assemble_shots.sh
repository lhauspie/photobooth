#!/bin/bash

root_folder="/home/pi/photobooth"

montage -background '#FF2525' $root_folder/shots/$1/*.jpg -tile 2x2 -geometry +20+20, $root_folder/PB_archive/$1.jpg
convert -bordercolor '#FF2525' -border 40x20 $root_folder/PB_archive/$1.jpg $root_folder/PB_archive/$1.jpg
composite -compose Over -gravity Center $root_folder/scripts/Template_center.png $root_folder/PB_archive/$1.jpg $root_folder/PB_archive/$1.jpg

