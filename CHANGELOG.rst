.. _intro_history:

=======
History
=======

Version 0.5.0 - Unreleased
--------------------------

* Removed support for Python<3.8;
* Added support for Python from 3.8 to 3.10;
* Removed useless requirement to ``six``;
* Implemented ``--serve`` option on ``page`` command to serve contents once the report
  has been built;
* Splitted utils in various modules;
* Modernized package configuration;
* Modernized makefile;
* Updated README;
* Added documentation;
* Added Github issue templates;
* Upgraded ``setup.cfg`` and project's ``__init__`` module to drop usage of
  ``pkg_resources`` in profit of importlib
  `#26 <https://github.com/sveetch/py-html-checker/issues/26>`_;

.. TODO:

    * [x] Server mode is fully implemented and working with 'page'
    * [x] Interface has been tested.
    * [-] Upgrade Nu Html library (there is no new release yet);
    * [ ] Upgrade requirements using 'pkg>=x.x.x' to modernize and help pip install;
    * [ ] Find a logo ?
    * [ ] Still have to implement '--serve' also on 'site' command;
    * [ ] Support of Sitemap index;
    * [ ] Create issue for each undone tasks;


Version 0.4.2 - 2022/03/17
--------------------------

Fix issue with currently used Jinja version (2.x) which did not pinned MarkupSafe
version but use a ``soft_unicode`` function which have been dropped since
MarkupSafe 2.1.0. This leaded to HTML export to be unavailable even with Jinja
installed. So until we migrate to Jinja 3.x, we pinned MarkupSafe to 2.0.1;


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

