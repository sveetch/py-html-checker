.. _Nu Html Checker (v.Nu): https://github.com/validator/validator
.. _Sitemap: http://www.sitemaps.org/

Py Html Checker
===============

This is an interface around `Nu Html Checker (v.Nu)`_ to check document
validation either from a list of pages or a `Sitemap`_.

Links
*****

* Download its `PyPi package <http://pypi.python.org/pypi/py-html-checker>`_;
* Clone it on its `Github repository <https://github.com/sveetch/py-html-checker>`_;

Requires
********

* Python>=3.4;
* Java>=8 (openjdk8 or oraclejdk8);
* Virtualenv (recommended but not mandatory);
* Pip (recommended but not mandatory);

Dependancies
************

* ``requests``;
* ``click>=7.0,<8.0`` (CLI only);
* ``colorama`` (CLI only);
* ``colorlog`` (CLI only);

Install
*******

::
    pip install py-html-checker[cli]

If you don't plan to use it from command line (like as a module) you can avoid
the ``cli`` part: ::

    pip install py-html-checker

Usage
*****

For a list of documents, you may either give file paths or URL: ::

    html-checker -v 5 page ping.html http://perdu.com foo/bar.html

Or for all documents from a `Sitemap`_: ::

    html-checker -v 5 site http://perdu.com/sitemap.xml

The sitemap path can be either a filepath or an url. Note than from a sitemap
file, documents file paths have to be absolute or relative to the current
directory where you have executed the command line.
