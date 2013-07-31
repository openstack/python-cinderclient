Cinder Client Style Commandments
=========================

- Step 1: Read the OpenStack Style Commandments
  https://github.com/openstack-dev/hacking/blob/master/HACKING.rst
- Step 2: Read on

Cinder Client Specific Commandments
----------------------------

General
-------
- Do not use locals(). Example::

    LOG.debug(_("volume %(vol_name)s: creating size %(vol_size)sG") %
              locals()) # BAD

    LOG.debug(_("volume %(vol_name)s: creating size %(vol_size)sG") %
              {'vol_name': vol_name,
               'vol_size': vol_size}) # OKAY

- Use 'raise' instead of 'raise e' to preserve original traceback or exception being reraised::

    except Exception as e:
        ...
        raise e  # BAD

    except Exception:
        ...
        raise  # OKAY

Text encoding
----------
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
