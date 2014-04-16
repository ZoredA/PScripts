PScripts
========
Note: colorama is not my project. It is just used by PrintDictionary and it is in general, a handy thing to have near. Here is the home page: https://pypi.python.org/pypi/colorama

A collection of little Python scripts that aid in my day to day life.

mRename is very useful for me, but I doubt it would be useful for anyone else reading this.

TableGenerator is very simple in what it does (generates a html table), but it is a simple, crude way of making one and it works.

RangeWorks is surprisingly complicated for what it does and unfortunately, it serves a very small simple niche, so most folk probably won't find it useful. That said, 
it does do some nifty things. Look in mRename to see how to use it interpret an incomplete range. Arguably its most useful (and most recent) feature is probably the collectionSize
function which returns something resembling the dimension of a given collection (if we treat the collection as a matrix that is). There are some caveats to it (performance likely being one),
but it is kind of cute.

PrintDictionary would be a bit more useful if it was a bit easier to use. I recommend sticking to using colorama by itself. PrintDictionary is quite powerful though.

moveImages DOES NOT WORK according to design. If I get the time, I will try to look at it again, but it is probably better to just a nice GUI program to do the same thing.
 
mRename
-------

###Introduction:

I really like using mPlayer/smPlayer for video playback. I also like taking screenshots with mPlayer/smPlayer.

Unfortunately, a feature that is lacking is the ability to give screen captures custom names.

Even if this feature was present, it would still not always be useful because you often don't want to deal 
with cumbersome file names in your screen shots.

mRename.py is a dirty little script that looks at a Screencaps folder for image files with
the template "shot%d" where %d is a number.

It then makes a copy of those screencaps in a different specified folder with a different
name and adds a counter as part of the name.

It then uses ImageMagick (www.imagemagick.org) to convert the .png files to .jpg to save space.
The .png files are then deleted.

This script is smart enough that it will check the output folder and figure out the largest number from a previous run
and use that + 1 as the starting counter for the current run.

Note: The original files stored in the Screencap folder will be deleted if the user tells it to delete them.

I added a feature that allows a file to be specified in the command line. This fill should include a list of names
and map each entry to some range. mRename will parse this file and move the specified images. It also attempts to interpret the
range specified in the file, so the range doesn't have to be complete.

The contents of the file would look something like this:

Show1 : 1 - 107
Show2 : - 181
Show3 : 185 - 186
Show4 : - 301
Show5 : - 414

where Show1 is the name of the folder the images are being moved to and renamed to. The First value after the colon indicates the starting screen shot and the value after the - indicates the
ending screen shot.

Note that there can be some numbers missing. These get interpreted by RangeWorks.py, so it would actually end up like so:
Show1 : 1 - 107
Show2 : 108 - 181
Show3 : 185 - 186
Show4 : 187 - 301
Show5 : 302 - 414

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
python rename.py [moveListFile]
```

###Future Plans:
* Add command line parameters for name/start number/end number so it doesn't go ask the user for input.
* Make the destination and perhaps even the source folder be configurable via command line parameters.
* Add a command line _silent_ option.
* Possibly make the output file name more flexible. Possibly add VLC style customizable syntax.


