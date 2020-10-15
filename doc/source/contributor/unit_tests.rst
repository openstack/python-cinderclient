==========
Unit Tests
==========

Cinderclient contains a suite of unit tests, in the cinderclient/tests/unit
directory.

Any proposed code change will be automatically rejected by the OpenStack
Jenkins server if the change causes unit test failures.

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
simply by specifying to just run py3 tests against a single test::

    tox -e py3 -- -n cinderclient.tests.unit.v2.test_volumes.VolumesTest.test_attach

Or all tests in the test_volumes.py file::

    tox -e py3 -- -n cinderclient.tests.unit.v2.test_volumes

For more information on these options and how to run tests, please see the
`stestr documentation <https://stestr.readthedocs.io/en/latest/index.html>`_.

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
