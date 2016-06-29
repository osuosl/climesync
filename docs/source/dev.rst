.. _dev:

Developer Documentation for Climesync
=====================================

.. contents::

Setting up the Development Environment
--------------------------------------

Climesync is developed using the `virtualenvwrapper`_ utility to manage versions
and dependencies. To install virtualenvwrapper, run

.. code-block:: none

    $ pip install virtualenvwrapper

To create a new virtualenv and install all of Climesync's dependencies, do

.. code-block:: none

    $ mkvirtualenv venv
    ...
    (venv) $ pip install -r requirements.txt

Testing Climesync
-----------------

To lint climesync for non-PEP8 compliance, run

.. code-block:: none
    
    (venv) $ flake8 climesync.py testing

To run unit tests, use this command:

.. code-block:: none

    (venv) $ nosetests

To enable `Pymesync test mode`_ when writing unit tests, call

.. code-block:: python
    
    connect(test=True)

instead of

.. code-block:: python

    connect()
    
.. _Pymesync test mode: http://pymesync.readthedocs.io/en/latest/testing.html

Function Documentation
----------------------

For the most part, Climesync functions match 1 to 1 with menu options.
However, there are several utility functions (Such as print_json and
get_fields) that help eliminate cluttered and unnecessary repeated code.

Detailed information on how to use these functions is included in the
docstrings inside the Climesync source code.
