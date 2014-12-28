MGD
===

MGD stand for ManGa Downloader.

It's command line tool for downloading manga from various site.

Actually, if you want something that do the job take a look to:

 - [mangareader-to-ebook][1]: a "simple" project that do the job
 - [manga_downloader][2]: a better looking one

State
---

Actually not working... and not much time to code.

Functionnals Objectives
===

 1. Store Meta-data in db file, and allow operation on it.
 2. when possible (default behaviour), store images in DB too.
 2. Being able to get / read one manga (ex: all "Monster") simply.
 3. Being able to generate multiple output (cbz/epub/pdf ...) without downloading all over again
    ex: all chapters in one epub with chapter delimitation etc...
 4. Make it multiplatform (Mac/Window/Linux)


Requirements
===

- [Python 3.4][6]
- [SQLAlchemy][3]
- [Requests][4]
- [SQLite][5]

Build
---

- [Versioneer][9]


Tests
---

- [unittest][8]
- [Pytest][7]


Personnal Purpose
===========

Having fun :)

And building a "nice and beautiful" project (with some docs, unitests etc...).

Use of sqlite, and requests and some other cool stuff.

Use of Python3.

Use of git.


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
