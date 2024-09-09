.. _virtualenv: https://virtualenv.pypa.io
.. _pip: https://pip.pypa.io
.. _Pytest: http://pytest.org
.. _Napoleon: https://sphinxcontrib-napoleon.readthedocs.org
.. _Flake8: http://flake8.readthedocs.org
.. _Sphinx: http://www.sphinx-doc.org
.. _tox: http://tox.readthedocs.io
.. _livereload: https://livereload.readthedocs.io
.. _twine: https://twine.readthedocs.io

.. _development_intro:

===========
Development
===========

py-html-checker is developed with:

* *Test Development Driven* (TDD) using `Pytest`_;
* Respecting flake and pip8 rules using `Flake8`_;
* `Sphinx`_ for documentation with enabled `Napoleon`_ extension (using
  *Google style*);
* `tox`_ to run tests on various environments;

Every requirements are available in package extra requirements.

.. _development_install:


System requirements
*******************

This will requires `Python`, `pip`_, `virtualenv`_, *GNU make* and some other common
system packages.

Lists below are the required basic development system packages and some other optional
ones.

.. Warning::
   Package names may differ depending your system.

* Git;
* Python (according version to the package setup);
* ``python-dev``;
* ``make``;

.. Hint::
   If your system does not have the right Python version as the default one, you should
   learn to use something like `pyenv <https://github.com/pyenv/pyenv>`_.

On Linux distribution
    You will install them from your common package manager like ``apt`` for Debian
    based distributions: ::

        apt install python-dev make

On macOS
    Recommended way is to use ``brew`` utility for system packages, some names
    can vary.

On Windows
    Windows is supported but some things may need some tricks on your own.


Deployment
**********

Once requirements are ready you can use the following commands: ::

    git clone https://github.com/sveetch/py-html-checker.git
    cd py-html-checker
    make install


Tests
*****

Unittests are made to works on `Pytest`_, a shortcut in Makefile is available
to start them on your current development install: ::

    make test

Tests are required to be done in the same spirit that the existing ones.

.. Warning::
    Tests are required to pass, always. Nothing is allowed to be merged or released
    with tests failures.

    New features should always comes with some new test coverage.

Tox
***

To ease development against multiple Python versions a tox configuration has
been added. You are strongly encouraged to use it to test your pull requests.

Just execute Tox: ::

    make tox

This will run tests for all configured Tox environments, it may takes some time so you
may use it only before releasing as a final check.


Documentation
*************

You can easily build the documentation from one Makefile action: ::

    make docs

There is Makefile action ``livedocs`` to serve documentation and automatically
rebuild it when you change documentation files: ::

    make livedocs

Then go on ``http://localhost:8002/`` or your server machine IP with port 8002.

.. Note::
    You need to build the documentation at least once before using  ``livedocs``.


Repository workflow
*******************

* Branch ``master`` is always in the last version release state. You never develop
  directly on it and only merge release once validated and released;
* A new development (feature, fix, etc..) always starts from ``development``;
* Each release has its own history branch like ``v1.2.3``;
* It is important that ``master`` and ``development`` stay correctly aligned;

A contributor starts a new branch called *a feature branch* (despite it is for a bug
fix, a feature or something else) that it will submit through a *Pull request*.


Resume for a contributor
------------------------

#. Start working from a new branch started from the last version of branch
   ``development``;
#. Commit and push your work to your branch;
#. Make a pull request for your branch with target on branch ``development``;
#. You are done.

As an example a contributor would work like this: ::

    git clone REPOSITORY
    git checkout development origin/development
    git checkout -b my_new_feature
    # ..Then implement your feature..
    git commit -a -m "[NEW] Added new feature X"
    git push origin my_new_feature

At this point contributor need to open a pull request for its feature branch.


Resume for a maintainer
------------------------

#. Validate a pull request from a contributor;
#. Merge validated branch into branch ``development``;
#. Make a new release (version bump, add changelog, etc..) into branch ``development``
   and push it;
#. Merge branch ``development`` into a new branch named after release version prefixed
   with character ``v`` like ``v1.2.3``;
#. Merge branch ``v1.2.3`` into branch ``master``;
#. Tag release commit with new version ``1.2.3``;
#. Push ``master`` with tags;

As an example a project maintainer would pull a feature branch and continue for
releasing it: ::

    # Merge validated new feature branch into development
    git checkout development
    git merge my_new_feature
    # ..Bump version and update Changelog
    git commit -a -m "[NEW] (v1.2.3) Release"
    git push origin development
    # ..Then merge new release into master
    git checkout master
    git merge development
    git tag -a 1.2.3 COMMIT-HASH
    git push --tags origin master
    # ..Create the version branch
    git checkout -b v1.2.3
    git push origin v1.2.3


Where ``1.2.3`` is dummy sample of a new version.

.. Note::
    Not every merged feature branch would trigger a new release process. It is common
    to only merge the feature branch in ``development`` and wait for some other ones
    before to release. In this case the maintainer would simply stop process once
    feature branch has been merged.

Releasing
*********

Before releasing, you must ensure about quality, use the command below to run every
quality check tasks: ::

    make quality

If quality is correct and after you have correctly pushed all your commits
you can proceed to release: ::

    make release

This will build the package release and send it to Pypi with `twine`_.
You will have to
`configure your Pypi account <https://twine.readthedocs.io/en/latest/#configuration>`_
on your machine to avoid to input it each time.


Contribution
************

* Every new feature or changed behavior must pass all quality tasks and must be
  documented (at least docstrings);
* Every feature or behavior must be compatible for all supported environment;
