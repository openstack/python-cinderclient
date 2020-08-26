================
Functional Tests
================

Cinderclient contains a suite of functional tests, in the cinderclient/
tests/functional directory.

These are currently non-voting, meaning that Jenkins will not reject a
patched based on failure of the functional tests. It is highly recommended,
however, that these tests are investigated in the case of a failure.

Running the tests
-----------------
Run the tests using tox, which calls ostestr via the tox.ini file.  To run all
tests simply run::

    tox -e functional

This will create a virtual environment, load all the packages from
test-requirements.txt and run all unit tests as well as run flake8 and hacking
checks against the code.

Note that you can inspect the tox.ini file to get more details on the available
options and what the test run does by default.

Running a subset of tests using tox
-----------------------------------
One common activity is to just run a single test, you can do this with tox
simply by specifying to just run py27 or py34 tests against a single test::

    tox -e functional -- -n cinderclient.tests.functional.test_readonly_cli.CinderClientReadOnlyTests.test_list

Or all tests in the test_readonly_clitest_readonly_cli.py file::

    tox -e functional -- -n cinderclient.tests.functional.test_readonly_cli

For more information on these options and how to run tests, please see the
`stestr documentation <https://stestr.readthedocs.io/en/latest/index.html>`_.

Gotchas
-------

The cinderclient.tests.functional.test_cli.CinderBackupTests.test_backup_create
and_delete test will fail in Devstack without c-bak service running, which
requires Swift. Make sure Swift is enabled when you stack.sh by putting this in
local.conf::

    enable_service s-proxy s-object s-container s-account
