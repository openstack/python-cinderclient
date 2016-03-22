==================
CINDERCLIENT Tests
==================

Unit Tests
==========

Cinderclient contains a suite of unit tests, in the cinderclient/tests/unit
directory.

Any proposed code change will be automatically rejected by the OpenStack
Jenkins server [#f1]_ if the change causes unit test failures.

Running the tests
-----------------
There are a number of ways to run unit tests currently, and there's a
combination of frameworks used depending on what commands you use.  The
preferred method is to use tox, which calls ostestr via the tox.ini file.
To run all tests simply run::

    tox

This will create a virtual environment, load all the packages from
test-requirements.txt and run all unit tests as well as run flake8 and hacking
checks against the code.

Note that you can inspect the tox.ini file to get more details on the available
options and what the test run does by default.

Running a subset of tests using tox
-----------------------------------
One common activity is to just run a single test, you can do this with tox
simply by specifying to just run py27 or py34 tests against a single test::

    tox -epy27 -- -n cinderclient.tests.unit.v2.test_volumes.VolumesTest.test_attach

Or all tests in the test_volumes.py file::

    tox -epy27 -- -n cinderclient.tests.unit.v2.test_volumes

For more information on these options and how to run tests, please see the
`ostestr documentation <http://docs.openstack.org/developer/os-testr/>`_.

Run tests wrapper script
------------------------

In addition you can also use the wrapper script run_tests.sh by simply
executing::

    ./run_tests.sh

This script is a wrapper around the testr testrunner and the flake8 checker.
Note that there has been talk around deprecating this wrapper and this method of
testing, it's currently available still but it may be good to get used to using
tox or even ostestr directly.

Documenation is left in place for those that still use it.

Flags
-----

The ``run_tests.sh`` script supports several flags. You can view a list of
flags by doing::

    run_tests.sh -h

This will show the following help information::
    Usage: ./run_tests.sh [OPTION]...
    Run cinderclient's test suite(s)

      -V, --virtual-env           Always use virtualenv.  Install automatically if not present
      -N, --no-virtual-env        Don't use virtualenv.  Run tests in local environment
      -s, --no-site-packages      Isolate the virtualenv from the global Python environment
      -r, --recreate-db           Recreate the test database (deprecated, as this is now the default).
      -n, --no-recreate-db        Don't recreate the test database.
      -f, --force                 Force a clean re-build of the virtual environment. Useful when dependencies have been added.
      -u, --update                Update the virtual environment with any newer package versions
      -p, --pep8                  Just run PEP8 and HACKING compliance check
      -P, --no-pep8               Don't run static code checks
      -c, --coverage              Generate coverage report
      -d, --debug                 Run tests with testtools instead of testr. This allows you to use the debugger.
      -h, --help                  Print this usage message
      --hide-elapsed              Don't print the elapsed time for each test along with slow test list
      --virtual-env-path <path>   Location of the virtualenv directory
                                   Default: $(pwd)
      --virtual-env-name <name>   Name of the virtualenv directory
                                   Default: .venv
      --tools-path <dir>          Location of the tools directory
                                   Default: $(pwd)

    Note: with no options specified, the script will try to run the tests in a virtual environment,
          If no virtualenv is found, the script will ask if you would like to create one.  If you
          prefer to run tests NOT in a virtual environment, simply pass the -N option.

Because ``run_tests.sh`` is a wrapper around testr, it also accepts the same
flags as testr. See the the documentation for details about these additional flags:
`ostestr documentation <http://docs.openstack.org/developer/os-testr/>`_.

.. _nose options documentation: http://readthedocs.org/docs/nose/en/latest/usage.html#options

Suppressing logging output when tests fail
------------------------------------------

By default, when one or more unit test fails, all of the data sent to the
logger during the failed tests will appear on standard output, which typically
consists of many lines of texts. The logging output can make it difficult to
identify which specific tests have failed, unless your terminal has a large
scrollback buffer or you have redirected output to a file.

You can suppress the logging output by calling ``run_tests.sh`` with the nose
flag::

    --nologcapture

Virtualenv
----------

By default, the tests use the Python packages installed inside a
virtualenv [#f2]_. (This is equivalent to using the ``-V, --virtualenv`` flag).
If the virtualenv does not exist, it will be created the first time the tests
are run.

If you wish to recreate the virtualenv, call ``run_tests.sh`` with the flag::

    -f, --force

Recreating the virtualenv is useful if the package dependencies have changed
since the virtualenv was last created. If the ``requirements.txt`` or
``tools/install_venv.py`` files have changed, it's a good idea to recreate the
virtualenv.

By default, the unit tests will see both the packages in the virtualenv and
the packages that have been installed in the Python global environment. In
some cases, the packages in the Python global environment may cause a conflict
with the packages in the virtualenv. If this occurs, you can isolate the
virtualenv from the global environment by using the flag::

    -s, --no-site packages

If you do not wish to use a virtualenv at all, use the flag::

    -N, --no-virtual-env

Gotchas
-------

**Running Tests from Shared Folders**

If you are running the unit tests from a shared folder, you may see tests start
to fail or stop completely as a result of Python lockfile issues. You
can get around this by manually setting or updating the following line in
``cinder/tests/conf_fixture.py``::

    CONF['lock_path'].SetDefault('/tmp')

Note that you may use any location (not just ``/tmp``!) as long as it is not
a shared folder.

.. rubric:: Footnotes

.. [#f1] See :doc:`jenkins`.

.. [#f2] See :doc:`development.environment` for more details about the use of
   virtualenv.
