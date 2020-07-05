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
* Virtualenv (recommended);
* Pip (recommended);

Dependancies
************

* ``requests``;
* ``click>=7.0,<8.0`` (CLI only);
* ``colorama`` (CLI only);
* ``colorlog`` (CLI only);
* ``Jinja2>=2.10,<3.0`` (Jinja only);
* ``Pygments`` (Jinja only);

Install
*******

::

    pip install py-html-checker[cli,jinja]

If you don't plan to use it from command line (like as a module) and for HTML
export you can avoid the ``cli`` and ``jinja`` parts: ::

    pip install py-html-checker

Usage
*****

Validate one or many pages
--------------------------

With the command ``page`` you can validate one or many pages. Command accept
one or many path and each path can be either an URL or a filepath (absolute or
relative from your current location): ::

    htmlcheck page ping.html
    htmlcheck page http://perdu.com
    htmlcheck page ping.html http://perdu.com foo/bar.html

Validate all path from a sitemap
--------------------------------

With the command ``site`` you can validate every page referenced in a
``sitemap.xml`` file. Command accept only one argument for the sitemap path
which can be either an URL or a filepath (absolute or relative from your
current location).

Note than for a sitemap file, its referenced urls must be absolute or relative
to your current location. For a sitemap url, its referenced urls must be an
absolute url (with leading ``http``): ::

    htmlcheck site sitemap.xml
    htmlcheck site http://perdu.com/sitemap.xml

Manage verbosity
----------------

Default commandline verbosity is set to "Info" level, you may set it to "Debug"
level to get also some more informations about command line work: ::

    htmlcheck -v 5 site sitemap.xml

Or a totally silent output (beware that not any error will be return to output
except commandline critical error): ::

    htmlcheck -v 0 site sitemap.xml

Common options
--------------

**--destination**
    Directory path where to write report files. If destination is not given,
    every files will be printed out. You can use a dot to write files to your
    current directory, a relative path or an absolute path. Path can start
    with `~` to point to your user home directory.
**--exporter**
    Select exporter format. Default format is ``logging``, it just printout
    report messages. There is also a ``json`` format to create JSON files for
    reports. And finally a ``html`` format to create HTML files.
**--pack/--no-pack**
    Pack reports into a single file or not. Default is to pack everything in
    a single file. 'no-pack' will create a file for each report and then an
    export summary. It is recommended to define a destination directory with
    '--destination' if you don't plan to use packed export, else every files
    will just be printed out in an unique output. This option has no effect
    with ``logging`` format.
**--safe**
    Invalid paths won't break execution of script and it will be able to
    continue to the end. This is mostly for rare usecase when invalid source
    encounter a bug from report parsing or from validator.
**--split**
    Execute validation for each path in its own distinct instance. Useful for
    very large path list which may take too long to display anything until
    every path has been validated. However, for small or moderate path list it
    will be longer than packed execution.
**--user-agent**
    A customer user-agent to use for every possible requests.
**--Xss**
    Java thread stack size. Useful in some case where you encounter error
    'StackOverflowError' from validator. Set it to something like '512k'.

Specific formats options
------------------------

html
....

**--template-dir**
    A path to a template directory for your custom templates. Your template
    directory must contains the summary, report and audit main templates and
    also a `main.css` file.


Specific 'site' options
-----------------------

**--sitemap-only**
    For ``site`` command only. This will only get and parse given sitemap path
    but without validating its items, useful to validate a sitemap before
    using it for validations.


CLI help
--------

See commandline helps for more details : ::

    htmlcheck -h
    htmlcheck page -h
    htmlcheck site -h
