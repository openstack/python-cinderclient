Cinder Client Style Commandments
================================

- Step 1: Read the OpenStack Style Commandments
  https://docs.openstack.org/hacking/latest/
- Step 2: Read on

Cinder Client Specific Commandments
-----------------------------------

General
-------
- Use 'raise' instead of 'raise e' to preserve original traceback or exception
  being reraised::

    except Exception as e:
        ...
        raise e  # BAD

    except Exception:
        ...
        raise  # OKAY

Release Notes
-------------
- Any patch that makes a change significant to the end consumer or deployer of
  an OpenStack environment should include a release note (new features, upgrade
  impacts, deprecated functionality, significant bug fixes, etc.)

- Cinder Client uses Reno for release notes management. See the `Reno
  Documentation`_ for more details on its usage.

.. _Reno Documentation: https://docs.openstack.org/reno/latest/

- As a quick example, when adding a new shell command for Awesome Storage
  Feature, one could perform the following steps to include a release note for
  the new feature::

    $ tox -e venv -- reno new add-awesome-command
    $ vi releasenotes/notes/add-awesome-command-bb8bb8bb8bb8bb81.yaml

  Remove the extra template text from the release note and update the details
  so it looks something like::

    ---
    features:
      - Added shell command `cinder be-awesome`  for Awesome Storage Feature.

- Include the generated release notes file when submitting your patch for
  review.
