.. _intro_history:

=======
History
=======

Version 0.4.1 - 2021/07/26
--------------------------

* Include a fix proposed by @acbaraka to enhance Window support, even it's not an
  official support;
* Clean validator output from a line information about environment variable
  ``_JAVA_OPTIONS``, close #22;
* Add Tox to dev requirements;
* Remove Python 3.5 support;
* Validate support for Python 3.6 to 3.8;


Version 0.4.0 - 2020/07/07
--------------------------

* Add this changelog;
* Upgrade to ``vnu==20.6.30``;
* Rename commandline name from ``html-checker`` to ``htmlcheck`` following this
  document `<https://smallstep.com/blog/the-poetics-of-cli-command-names/>`_;
* Add ``twine`` in extra requirements ``dev`` and use it in for Makefile
  ``release`` action;


Version 0.3.0 - 2020/02/10
--------------------------

First usable version with HTML and JSON exporters and every required vnu option
support.

