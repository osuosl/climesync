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

.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper


Testing Climesync
-----------------

To lint climesync for non-PEP8 compliance, run

.. code-block:: none

    (venv) $ flake8 climesync.py commands.py util.py testing

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


Program Flow Overview
---------------------


Interactive Mode
~~~~~~~~~~~~~~~~

.. code-block:: none

    +-------------+
    | Entry Point |
    +-------------+
           |
           |
           V
       +------+          +--------+
       | Main | <------> | Docopt |
       |      |          +--------+
       |      |
       |      |          +-------------+
       |      | <------> | Read Config |
       |      |          +-------------+
       |      |
       |      |          +---------------------+          +-------------+
       |      | <------> | Connect and Sign In | <------> | Build Cache |
       +------+          +---------------------+          +-------------+
           |
           |     | Command
           V     V
    +------------------+          +---------------------------+
    | Interactive Menu | <------> | Receive and Parse Command |
    +------------------+          +---------------------------+
           |     |
           |     V "Quit" Command
           V
    +-------------------+          +---------------------------+
    | climesync_command | <------> | User Authentication Check |
    +-------------------+          +---------------------------+
           |
           |
           V
      +---------+          +----------------+          +---------------------+
      | Command | <------> | Get user input | <------> | Validate user input |
      |         |          +----------------+          +---------------------+
      |         |
      |         |          +---------------+
      |         | <------> | Make API Call |
      |         |          +---------------+
      |         |
      |         |          +------------------------------------------------+
      |         | <------> | Handle API Response (Print/Output to CSV/etc.) |
      +---------+          +------------------------------------------------+
           |
           V Interactive Menu


Scripting Mode
~~~~~~~~~~~~~~

.. code-block:: none

    +-------------+
    | Entry Point |
    +-------------+
           |
           |
           V
       +------+          +--------+
       | Main | <------> | Docopt |
       |      |          +--------+
       |      |
       |      |          +-------------+
       |      | <------> | Read Config |
       |      |          +-------------+
       |      |
       |      |          +---------------------+          +-------------+
       |      | <------> | Connect and Sign In | <------> | Build Cache |
       +------+          +---------------------+          +-------------+
           |
           |
           V
    +----------------+          +-------------------+
    | Scripting Mode | <------> | Lookup subcommand |
    +----------------+          +-------------------+
           |
           |
           V
    +-------------------+          +--------+          +-------------------------+
    | climesync_command | <------> | Docopt | <------> | Fix argument formatting |
    |                   |          +--------+          +-------------------------+
    |                   |
    |                   |          +-----------------------------------+
    |                   | <------> | Construct command-specific kwargs |
    +-------------------+          +-----------------------------------+
           |
           |
           V
      +---------+          +---------------+
      | Command | <------> | Make API Call |
      |         |          +---------------+
      |         |
      |         |          +------------------------------------------------+
      |         | <------> | Handle API Response (Print/Output to CSV/etc.) |
      +---------+          +------------------------------------------------+
           |
           V Exit


Docopt
------

`docopt`_ is a module that creates command line parsers from docstrings. In
interactive mode, docopt is used once to parse command line arguments such
as username and password, but in scripting mode it's called twice. The first
time it's called, it uses the main docstring to parse any global options, and
if it sees that a command has been provided then the arguments after the
command name are given to the command, which uses its own docstring to
parse arguments and options.


The @climesync_command Decorator
--------------------------------

If you don't know what a decorator is in Python, `this article`_ is a good
starting point to understanding what they are and how they are used. In
essence, decorators are Python's form of metaprogramming that are somewhat
analagous to C/C++ #define macros.

Every Climesync command that is accessible from both interactive mode and
scripting mode uses a decorator as a wrapper to handle both use cases. If the
command is called in scripting mode, it handles calling :code:`docopt()` to parse
command line arguments as well as :code:`util.fix_args()` to fix the names of the
parsed arguments. If the program is in interactive mode, the decorator simply
calls the command.

The decorator takes two arguments: :code:`select_arg` and :code:`optional_args`.
:code:`optional_args` is the simpler of the two arguments. It simply indicates
whether options that are left blank should be included as non-truthy values
(such as :code:`None`) or simply left out of the dictionary that is given to Pymesync.

:code:`select_arg` is slightly more complicated. Certain Pymesync methods
don't just take a dictionary of values and also require that another keyword
argument be given to select a specific object (The most notable examples being
the :code:`update_*()` methods). Since there's no good way in docopt to distinguish
these select arguments from other arguments that do get put in the values
dictionary, these arguments must be specified to the decorator so it handles
them correctly.

Because some commands can't be called in scripting mode (Such as :code:`connect()`
and :code:`sign_in()`, they don't have the decorator. In the command_lookup table,
this is shown by putting :code:`None` for the scripting mode name

.. _this article: http://www.artima.com/weblogs/viewpost.jsp?thread=240808


The @test_command Decorator
---------------------------

In some test cases for core Climesync commands the @test_command decorator
is used to factor out repeated code because the format those tests follow are
so similar.

The decorator performs these actions:
    #. Authenticate and set up mocks for user input
    #. Run the command to be tested
    #. Compare the actual output with an expected output

The test data for these tests is located in :code:`testing/test_data.py`.


Function Documentation
----------------------

For the most part, Climesync functions match 1 to 1 with menu options.
However, there are several utility functions (Such as print_json and
get_fields) that help eliminate cluttered and unnecessary repeated code.

Detailed information on how to use these functions is included in the
docstrings inside the Climesync source code.
