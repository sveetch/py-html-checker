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

Validate one or many pages
--------------------------

With the command ``page`` you can validate one or many pages. Command accept
one or many path and each path can be either an URL or a filepath (absolute or
relative from your current location): ::

    html-checker page ping.html
    html-checker page http://perdu.com
    html-checker page ping.html http://perdu.com foo/bar.html

Validate all path from a sitemap
--------------------------------

With the command ``site`` you can validate every page referenced in a
``sitemap.xml`` file. Command accept only one argument for the sitemap path
which can be either an URL or a filepath (absolute or relative from your
current location).

Note than for a sitemap file, its referenced urls must be absolute or relative
to your current location. For a sitemap url, its referenced urls must be an
absolute url (with leading ``http``): ::

    html-checker site sitemap.xml
    html-checker site http://perdu.com/sitemap.xml

Common page and site options
----------------------------

**--user-agent**
    A customer user-agent to use for every possible requests.
**--Xss**
    Java thread stack size. Useful in some case where you encounter error
    'StackOverflowError' from validator. Set it to something like '512k'.
**--safe**
    Invalid paths won't break execution of script and it will be able to
    continue to the end.
**--split**
    Execute validation for each path in its own distinct instance. Useful for
    very large path list which may take too long to display anything until
    every path has been validated. However, for small or moderate path list it
    will be longer than packed execution.
**--sitemap-only**
    For ``site`` command only. This will only get and parse given sitemap path
    but without validating its items, useful to validate a sitemap before
    using it for validations.

See commandline helps for more details : ::

    html-checker -h
    html-checker page -h
    html-checker site -h
