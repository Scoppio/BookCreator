
# BookCreator3 - BookCreator for Python 3.5
# BookCreator
A scrapper that takes an online book from ORilley and turns into an epub book, because I want to read'em in my nook, away from my computer, and since I know python I figured out it could not be that hard...

# HOW TO INSTALL!

* Dependencies:
- LMXL
- Ebooklib
- BeatifulSoup [bs4]

It is a bit tricky... you need to install LXML, if you are using windows I suggest you to use the precompiled module [ www.lfd.uci.edu/~gohlke/pythonlibs/#lxml ]
To install epublib you will have to install using the project present in the github. Very easy, just download the master file [ https://github.com/aerkalov/ebooklib ] open the zip file and run your favorite installer, my tool of trade is pip so I run "pip install setup.py".
And finally, run "pip install bs4" and that is all.

##It is quite simple actually
The script is the "bookworm.py", it uses urllib2 and bs4 to lookup the html file in the web, download only the important part of it, captures the chapter name and sum it all up to create an epub file using the ebooklib (awesome lib this one! I'll probably create one that reads docstrings and creates the documentation of a python script with it!)

The script itself depends on the html file you want to read, and it must be online, it can work the chapters with local files but if a chapter is missing it will automatically copy the html and write it locally with the same name ofthe html it was reading.

##Features
* Easy to use
* Fast to modify to download other books
* Can be used to turn blogs into books! (requires a little bit of tinkering, contact me if you need help)
* Reliable
* Python 3.5! <3
