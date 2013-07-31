PScripts
========

A collection of little Python scripts that aid in day to day life.

mRename
-------

###Introduction:

I really like using mPlayer/smPlayer for video playback. I also like taking screenshots with mPlayer/smPlayer.

Unfortunately, a feature that is lacking is the ability to give screen captures custom names.

Even if this feauture was present, it would still not always be useful because you often don't want to deal 
with cumbersome file names in your screen shots.


mRename.py is a dirty little script that looks at a Screencaps folder for image files with
the template "shot%d" where %d is a number.


It then makes a copy of those screencaps in a different specified folder with a different
name and adds a counter as part of the name.

It then uses ImageMagick (www.imagemagick.org) to convert the .png files to .jpg to save space.
The .png files are then deleted.

Note: The original files stored in the Screencap folder are not deleted.

###Requirements:

* Python 3.X
* ImageMagick needs to be installed (not the Python library version, just the regular command line version).
* ImageMagick also needs to be added to the system path.

The only ImageMagick command this script runs is:
```bash
mogrify -format jpg *.png
```

###Usage:
```bash
python rename.py
```

###Future Plans:
* Add command line parameters for name/start number/end number so it doesn't go ask the user for input.
* Make the destination and perhaps even the source folder be configurable via command line parameters.
* Add a command line _silent_ option.
* Possibly make the output file name more flexible. Possibly add VLC style customizable syntax.


