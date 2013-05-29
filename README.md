PScripts
========

A collection of little Python scripts that aid in day to day life.

mRename
=======

Requirements:

Python 3.X
ImageMagick needs to be installed (not the Python library version, just the regular command line version).
ImageMagick also needs to be added to the system path.

The only ImageMagick command this script runs is:

mogrify -format jpg *.png

I really like using mPlayer/smPlayer for video playback. Unfortunately, a feauture
that is lacking is the ability to give screen captures custom names.
Even if this feauture was present, it would still not always be useful because you often
don't want to deal with the cumbersome file names.


mRename.py is a dirty little script that looks at a Screencaps folder for image files with
the template "shot%d" where %d is a number.


It then makes a copy of those screencaps in a different specified folder with a different
name and adds a counter as part of the name.

It then uses ImageMagick (www.imagemagick.org) to convert the .png files to .jpg to save space.
The .png files are then deleted.

Note: The original files stored in the Screencap folder are not deleted.
