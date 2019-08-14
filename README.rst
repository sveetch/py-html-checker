.. _Nu Html Checker (v.Nu): https://github.com/validator/validator


PyJudas
=======

Currently this tool use a ``sitemap.xml`` file (or JSON in a specific format)
to know about web page to validate with the `Nu Html Checker (v.Nu)`_.

Links
*****

* Download its `PyPi package <http://pypi.python.org/pypi/py-judas>`_;
* Clone it on its `Github repository <https://github.com/sveetch/py-judas>`_;

Requires
********

* Python>=3.4;
* Virtualenv;
* Pip;
* Java>=8 (openjdk8 or oraclejdk8);

Dependancies
************

* ``requests``;

Install
*******

``py-judas`` package is currently not released yet on Pypi so to
install it you will need to do something like: ::

    pip install py-judas.git

However in this way it will only usable as Python module, you won't have
command line requirements.

To have command line working you will need to do instead: ::

    pip install py-judas.git[cli]
