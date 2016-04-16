from bs4 import BeautifulSoup
from ebooklib import epub
import urllib2
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_PATH = os.path.join(BASE_PATH, 'downloads')
if not os.path.isdir(DOWNLOADS_PATH):
    print 'CREATING DOWNLOADS_PATH ({})'.format(DOWNLOADS_PATH)
    os.mkdir(DOWNLOADS_PATH)

#http://eloquentjavascript.net/index.html next try
#http://chimera.labs.oreilly.com/books/1234000000754/index.html
#http://chimera.labs.oreilly.com/books/1230000000393/index.html

def getOrreily (url="http://chimera.labs.oreilly.com/books/1234000000754/index.html"):
    """
    url must be of the index of an oreilly internet ebook
    """
    eBook = epub.EpubBook()
    
    resp = get_page(url)
    soup = BeautifulSoup(resp, from_encoding="UTF-8")
    
    url2 = url[:url.index("index")]

    chapters = ['']
    authors = []
    links = []
    book = {}

    book["Title"] = soup.find('h1', class_="title").getText()

    for author in soup.find_all("h3", class_="author"):
        authors.append(author.getText())

    book["Authors"] = authors
    book["TOC"] = str(soup.find('div', class_="toc"))
    
    with open(os.path.join(DOWNLOADS_PATH, "TOC.html"), "w") as text_file:
                text_file.write("<!-- " + book["Title"] + " -->\n")
                text_file.write(book["TOC"])

    for link in soup.find('div', class_="toc").find_all('a', href=True):
        if "#" not in link['href']:
            if 'pr' in link['href']:
                links.append(link['href'])

            if 'ch' in link['href']:
                links.append(link['href'])


    eBook.set_identifier(book["Title"])
    eBook.set_title(book["Title"])
    eBook.set_language("en")

    for author in book["Authors"]:
        eBook.add_author(author)

    f_ = os.listdir(DOWNLOADS_PATH)
        
    for link in links:
        if link in f_:
            print "local file:", link
            with open(os.path.join(DOWNLOADS_PATH, link), "r") as text_file:                  
                resp = text_file.read()    
        else:
            print "downloading file:", link
            resp = get_page(url2+link)
                        
        soup = BeautifulSoup(resp, from_encoding="UTF-8")

        try:
            c = epub.EpubHtml(title=soup.find('h1', class_="title").getText(), file_name=link, lang='en')
            c.content = createChapter(url2+link, link)
            chapters.append(c)
            eBook.add_item(c)
        except AttributeError:
            c = epub.EpubHtml(title=soup.find('h2', class_="title").getText(), file_name=link, lang='en')
            c.content = createChapter(url2+link, link)
            chapters.append(c)
            eBook.add_item(c)

    eBook.toc = chapters

    eBook.add_item(epub.EpubNcx())
    eBook.add_item(epub.EpubNav())


    # define css style
    style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
'''

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    eBook.add_item(nav_css)

    # create spine
    eBook.spine = chapters

    # create epub file
    epub.write_epub(book["Title"]+'.epub', eBook, {})    

def get_page(url):
    """ loads a webpage into a string """
    src = ''
    req = urllib2.Request(url)

    try:
        response = urllib2.urlopen(req)
        chunk = True
        while chunk:
            chunk = response.read(1024)
            src += chunk
        response.close()
    except IOError:
        print 'can\'t open',url 
        return src

    return src

def createChapter(url, chapter):

    response = urllib2.urlopen(url)
    webContent = str(response.read())

    a = webContent.index("section")-1
    b = webContent.index("</section>")+10
    chunk = webContent[a : b]    
    chunk = chunk.replace("http://chimera.labs.oreilly.com/books/1230000000393/", "")
    with open(os.path.join(DOWNLOADS_PATH, chapter), "w") as text_file:
        text_file.write(chunk)

    return chunk


if __name__ == '__main__':
    #argparse
    getOrreily()