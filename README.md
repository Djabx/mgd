[![Build Status](https://travis-ci.org/Djabx/mgd.svg?branch=develop)](https://travis-ci.org/travis-ci/travis-web)

# MGD


MGD stand for ManGa Downloader.

It's command line tool for downloading manga from various site.

Actually, if you want something that do the job take a look to:

 - [mangareader-to-ebook][1]: a "simple" project that do the job
 - [manga_downloader][2]: a better looking one

# State

It should works.

# Install


First you need [Python 3.4][6].

Then you can:

	git clone https://github.com/Djabx/mgd.git
	cd mgd
	python3 setup.py install


# Usage

	$ mgd -h
	usage: mgd [-h] [--data D\1
	           [-b BOOK_NAME] [-s SITE_NAME] [-i BOOK_ID] [-sc CHAPTER_START]
	           [-ec CHAPTER_END] [--site | -l | -lf | -f | -u | -d | -w]
	           [--cbz | --db | --flat | --flat-dir] [-o OUTPUT]

	optional arguments:
	  -h, --help            show this help message and exit
	  --data DATA_STORE     the output where to store all data (default to:
	                        "/localtion/mgd_store.db")
	  -v, --verbose         Enable verbose output
	  --site                Liste all known site with their id (disable sync
	                        operations).
	  -l, --list            List all know book (disable sync operations)
	  -lf, --list-followed  List followed book (disable sync operations)
	  -f, --follow          Mark as follow every book found
	  -u, --unfollow        Mark as unfollow every book found. (Disable sync
	                        operations)
	  -d, --delete          Delete every book found. (Disable sync operations)
	  -w, --web             Open web browser on it. (Disable sync operations)
	  --cbz                 Export as "cbz".
	  --db                  Export as "db".
	  --flat                Export as "flat".
	  --flat-dir            Export as "flat-dir".
	  -o OUTPUT, --output-dir OUTPUT
	                        The output directory path during export. (default to:
	                        "/localtion/export_output")

	sync level:
	  -sm, --meta           Sync and update meta data (list of books, etc.)
	  -ss, --struct         Sync structures of followed books (chapters, page
	                        structure etc.)
	  -si, --images         Sync all images
	  -sa, --all            Sync meta data, structures and images; equal to -sm
	                        -ss -si (default: True with action "follow" or
	                        "export")
	  -sn, --none           Do not sync anything, disable -sa / -ss / -sm / -si
	                        (default: True with others actions than "follow" or
	                        "export")

	selection:
	  -a, --all-books       Selection all books followed.
	  -b BOOK_NAME, --book-name BOOK_NAME
	                        Selection of books with the given name (use % for any)
	  -s SITE_NAME, --site-name SITE_NAME
	                        Selection of book from the given site (use % for any)
	  -i BOOK_ID, --book-id BOOK_ID
	                        Selection of book with the given id.
	  -sc CHAPTER_START, --start-chapter CHAPTER_START
	                        The chapter to start with (included). (only with -f or
	                        no actions)
	  -ec CHAPTER_END, --end-chapter CHAPTER_END
	                        The chapter to end with (included); even if newer
	                        chapters appears, we will skip them (only with -f or
	                        no actions)


# User case

## Search for a book

Search for a book that begin with "nar":

	mgd -b nar%

Output something like this:

	<id> <Manga Name> on <Site name>

Exemple:

	34412   Nar Kiss on Manga Here
	25120   Narutaru on Manga Here
	35013   Narutaru on Manga reader
	24538   Naruto on Manga Here
	34777   Naruto on Manga reader

## Follow a book

If your search give only one result just add `-f` to follow or you can use id like this:

	mgd -i 34412 -f

## Follow a book from a chapter

If your want to follow a book from a certain chapter (here 2):

	mgd -i 34412 -f -sc 2

## Follow a book until a chapter

If your want to follow a book until a chapter (here 3) (it must exist):

	mgd -i 34412 -f -ec 3


## Export as cbz

	mgd -i 34412 --cbz


# Functionnals Objectives

 1. Store Meta-data in db file, and allow operation on it.
 2. when possible (default behaviour), store images in DB too.
 2. Being able to get / read one manga (ex: all "Monster") simply.
 3. Being able to generate multiple output (cbz/epub/pdf ...) without downloading all over again
    ex: all chapters in one epub with chapter delimitation etc...
 4. Make it multiplatform (Mac/Window/Linux)


# Requirements

- [Python 3.4][6]
- [SQLAlchemy][3]
- [Requests][4]
- [SQLite][5]

# Build

- [Versioneer][9]


# Tests

(There will be some... one day... maybe)

- [unittest][8]
- [Pytest][7]


# Personnal Purpose

- [x] Having fun :)
- [ ] And building a "nice and beautiful" project (with some docs, unitests etc...).
- [ ] Use of sqlite, and requests and some other cool stuff.
- [x] Use of Python3.
- [x] Use of git.


Download manga from mangareader and build cbz, epub etc...

----------

  [1]: https://github.com/saturngod/mangareader-to-ebook "mangareader-to-ebook on Github"
  [2]: https://github.com/jiaweihli/manga_downloader "manga_downloader on Github"
  [3]: http://www.sqlalchemy.org/ "SQLalchemy"
  [4]: http://docs.python-requests.org/ "Requests"
  [5]: https://www.sqlite.org/ "SQLite"
  [6]: http://python.org/ "Python"
  [7]: http://pytest.org/ "PyTest"
  [8]: https://docs.python.org/2/library/unittest.html "unittest"
  [9]: https://github.com/warner/python-versioneer "Python versioneer"
