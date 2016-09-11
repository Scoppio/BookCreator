# BookCreator Script "BookWorm"
#
# Created by Lucas Scoppio
# Twitter @developercoppio
# 
# Do what you want cuz a pirate is free! YARRR!!!
# But don't forget to be nice, the world is lacking nice people
#

from bs4 import BeautifulSoup
from ebooklib import epub
from requests import get
import time
import argparse
import os

""" Slugfy imports """
import re
import unicodedata


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_PATH = os.path.join(BASE_PATH, 'downloads')
if not os.path.isdir(DOWNLOADS_PATH):
    print( 'CREATING DOWNLOADS_PATH ({})'.format(DOWNLOADS_PATH))
    os.mkdir(DOWNLOADS_PATH)

STYLE_PATH = os.path.join(BASE_PATH, 'style')    
if not os.path.isdir(STYLE_PATH):
    print( 'CREATING STYLE_PATH ({})'.format(STYLE_PATH))
    os.mkdir(STYLE_PATH)

VERBOSE = False
LANGUAGE = "en"
_style_ = "style.css"


def slugify(string):
    """A generic slugifier utility (currently only for Latin-based scripts).

    Slugify a unicode string.

    Example:

        >>> slugify(u"Héllø Wörld")
        u"hello-world"

    """

    return re.sub(r'[-\s]+', '-',
            (re.sub(r'[^\w\s-]', '',string).strip().lower()))


def getDataForEbook(url):
    """
    For now the url must be of the index of an oreilly internet ebook
    I plan to create a template file that will allow this script to read from just about
    any blog or website and turn it into an ebook.
    with the URL the script will look for the webpage and load it into memory to create
    the book Table of Contents, and after that it will create each chapter separately in its
    own folder, and to finish it up, it will wrap all into a single epub file.

    chapters  type: array[str]
               var: It will hold the information of all the chapters of the book
                    May in the future become a problem if the amount of data is too large
                    for it to handle

    authors   type: array[str]
               var: Keeps the names of the authors

    links     type: array[str]
               var: holds the links of every chapter for the ebook

    book      type: set{}
               var: Container for many important metadata for the ebook

    book_slug type: unicode
               var: slugify the url

    book_download_path 
              type: str
               var: the path of the download folder for the book to be created

    eBook     type: ebooklib
               var: constructor of the ebook
    """
    #creation of the variables necessary to create the ebook
    chapters = ['']
    authors = []
    links = []
    book = {}

    # first it will drop "http[s]://" and "index.html", if present:
    simplified_url = url.split('://')[-1].split('index.html')[0]
    if VERBOSE:
        print( 'simplified url:', simplified_url)
    #then we will create the book folder... turns out it has to be unicode, so we fix that here
    book_slug = slugify(simplified_url)#slugify(unicode(simplified_url, "utf-8"))
    book_download_path = os.path.join(DOWNLOADS_PATH, book_slug)
    #in case the book folder is not present, it will create one.
    if not os.path.isdir(book_download_path):
        os.mkdir(book_download_path)
        if VERBOSE:
            print( 'CREATING book_download_path ({})'.format(book_download_path))

    #Creating eBook creator
    eBook = epub.EpubBook()
    #Capturing the url to run BS4 on it
    resp = get_page(url)
    soup = BeautifulSoup(resp, "lxml", from_encoding="UTF-8")
    
    #url_root is the root of the book, where you find the table of contents (the link for all the chapters)
    url_root = url[:url.index("index")]
    #now we need to find the title of the book, usually it is an h1 with class "title"
    
    book["Title"] = soup.find('h1', class_="title").getText()

    #capture the authors of the book and put all to the authors ina variable to put into the metadata
    for author in soup.find_all("h3", class_="author"):
        authors.append(author.getText())
    #this is the metadata
    book["Authors"] = authors
    #load the whole section "table of contents" (toc) into the container
    book["TOC"] = str(soup.find('div', class_="toc"))

    #creates the TOC.html of the book
    with open(os.path.join(book_download_path, "TOC.html"), "w") as text_file:
                text_file.write("<!-- " + book["Title"] + " -->\n")
                text_file.write(book["TOC"])

    #to select the chapters it will look inside the TOC for links for chapters
    #those are prepared to capture only the chapters without the # markups and
    #only following the ORilley chapter names.
    for link in soup.find('div', class_="toc").find_all('a', href=True):
        if "#" not in link['href']:
            if 'pr' in link['href']:
                links.append(link['href'])

            if 'ch' in link['href']:
                links.append(link['href'])

    #setup the metadata
    eBook.set_identifier(book["Title"])
    eBook.set_title(book["Title"])   
    eBook.set_language(LANGUAGE)
    #adding the authors into ebook metadata
    for author in book["Authors"]:
        eBook.add_author(author)

    #look for the files inside the book downloaded path
    f_ = os.listdir(book_download_path)
    #and then run the links looking for each one inside the local path looking for files missing.
    for link in links:
        if link in f_:
            print( "Local file found:", link)
            with open(os.path.join(book_download_path, link), "r") as text_file:
                resp = text_file.read()
        else:
            print( "Downloading file:", link)
            resp = get_page(url_root + link)

        soup = BeautifulSoup(resp, "lxml", from_encoding="UTF-8")

        try:
            c = epub.EpubHtml(title=soup.find('h1', class_="title").getText(), file_name=link, lang='en')
            c.content = createChapter(url_root, link, book_download_path, resp)
            chapters.append(c)
            eBook.add_item(c)
        except AttributeError:
            c = epub.EpubHtml(title=soup.find('h2', class_="title").getText(), file_name=link, lang='en')
            c.content = createChapter(url_root, link, book_download_path, resp)
            chapters.append(c)
            eBook.add_item(c)

    eBook.toc = chapters

    eBook.add_item(epub.EpubNcx())
    eBook.add_item(epub.EpubNav())

    # define css style
    style = ""
    with open(os.path.join(STYLE_PATH, _style_), "r") as text_file:
                style = text_file.read()

    if VERBOSE:
        print( "Applying style", _style_)
    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    eBook.add_item(nav_css)

    # create spine
    eBook.spine = chapters
    time_elapsed = time.time()
    if VERBOSE:
        print( "Starting book creation...")
    # create epub file
    epub.write_epub(os.path.join( DOWNLOADS_PATH, book["Title"] + '.epub'), eBook, {})
    print( "Done,", os.path.join( DOWNLOADS_PATH, book["Title"] + '.epub'), "created!")
    print( "Time elapsed", time.time() - time_elapsed)

def get_page(url):
    """ loads a webpage into a string, reading it in chunks """
    src = ''
    #req = urllib2.Request(url)
    if VERBOSE:
        print( "GET PAGE:", url)
    #we have to try it, there is no other way to do it properly, because we may have timeouts
    try:
        result = get(url)
        src = result.content
    except IOError:
        #in case of url error we throw the error message
        print( 'can\'t open', url)
    except Exception as e:
        import traceback
        print('generic exception:', e)

    #return the content in src

    return src


def createChapter(url, chapter, book_download_path, response):
    """
    The url root is received, the name of the chapter is also taken to reach the correct page.
    Chapter is both the chapter and file extension - ex.: chapter01.html

    book_download_path is the path for the folder for the specific book.    
    """
    
    #after loading it to response, the data is turn into string and loaded to webContent
    webContent = str(response)
    #Unfortunatelly bs4 and urllib2 are causing problems to load only stuff inside the special markups
    #the best way to deal with it is directly manipulating the strings with native string operations
    #<xgh>
    a = webContent.index(TAG) - 1
    b = webContent.index("</"+TAG+">") + (len(TAG)+3)
    chunk = webContent[a:b]
    chunk = chunk.replace(url, "")
    #</xgh>
    if VERBOSE:
        print( "Writing", chapter, "to memory")
    #After all of that, the juicy stuff is written to a file that can later be modified
    with open(os.path.join(book_download_path, chapter), "w") as text_file:
        text_file.write(chunk)
    #Return the juice to the caller
    return chunk

if __name__ == '__main__':
    #EXAMPLE LINKS TO USE
    # http://eloquentjavascript.net/index.html next try
    # http://chimera.labs.oreilly.com/books/1234000000754/index.html
    # http://chimera.labs.oreilly.com/books/1230000000393/index.html
    # http://chimera.labs.oreilly.com/books/1230000000393/index.html
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="url of the webpage to be converted into ebook",
                    default="http://chimera.labs.oreilly.com/books/1234000000754/index.html")
    parser.add_argument("-l", "--language", help="select ebook language, defaulte is 'en'",
                    default="en")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true", default=True)
    parser.add_argument("-t", "--tag", help="Tag used in the webpage to define the start/end of the text of interest",
                    default="section")
    parser.add_argument("-css", "--style", help="css file inside style folder to change the ebook formating style",
                    default="style.css")
    args = parser.parse_args()

    _style_ = "style.css" #args['style']
    TAG = "section"       # args['tag']
    LANGUAGE = "en"       # args['language']
    VERBOSE = True        # args['verbose']

    if VERBOSE:
        print( "verbosity turned on")
        print( "Style loaded:", _style_)
        print( "Language loaded:", LANGUAGE)
        print( "Tag for section is", TAG)

    print( "Running", os.path.basename(__file__))
    getDataForEbook("http://chimera.labs.oreilly.com/books/1234000000754/index.html") # args['url']