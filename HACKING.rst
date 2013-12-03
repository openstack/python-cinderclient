Cinder Client Style Commandments
================================

- Step 1: Read the OpenStack Style Commandments
  http://docs.openstack.org/developer/hacking/
- Step 2: Read on

Cinder Client Specific Commandments
-----------------------------------

General
-------
- Use 'raise' instead of 'raise e' to preserve original traceback or exception being reraised::

    except Exception as e:
        ...
        raise e  # BAD

    except Exception:
        ...
        raise  # OKAY

Text encoding
-------------
- All text within python code should be of type 'unicode'.

    WRONG:

    >>> s = 'foo'
    >>> s
    'foo'
    >>> type(s)
    <type 'str'>

    RIGHT:

    >>> u = u'foo'
    >>> u
    u'foo'
    >>> type(u)
    <type 'unicode'>

- Transitions between internal unicode and external strings should always
  be immediately and explicitly encoded or decoded.

- All external text that is not explicitly encoded (database storage,
  commandline arguments, etc.) should be presumed to be encoded as utf-8.

    WRONG:

    mystring = infile.readline()
    myreturnstring = do_some_magic_with(mystring)
    outfile.write(myreturnstring)

    RIGHT:

    mystring = infile.readline()
    mytext = s.decode('utf-8')
    returntext = do_some_magic_with(mytext)
    returnstring = returntext.encode('utf-8')
    outfile.write(returnstring)

Release Notes
-------------
- Each patch should add an entry in the doc/source/index.rst file under
  "MASTER".

- On each new release, the entries under "MASTER" will become the release notes
  for that release, and "MASTER" will be cleared.

- The format should match existing release notes.  For example, a feature::

    * Add support for function foo

  Or a bug fix::

    .. _1241941: http://bugs.launchpad.net/python-cinderclient/+bug/1241941
