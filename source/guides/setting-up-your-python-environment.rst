.. _baseline-python-environment:

========================================
Setting up a baseline Python environment
========================================

Python packaging commands are easiest to reason about when the Python
interpreter, ``pip``, and installed command-line tools all refer to the same
environment. This guide establishes a simple baseline that the other
packaging guides can build on.

Before you begin
================

You should have:

* access to a command prompt or terminal;
* a supported Python interpreter;
* ``pip`` available for that interpreter; and
* permission to create a virtual environment in your project directory.

If Python is not installed yet, use the
`Python downloads page <https://www.python.org/downloads/>`__ or your
operating system's supported installation method. On Linux, also see
:doc:`installing-using-linux-tools`.

Create an isolated environment
==============================

Using a virtual environment keeps project packages separate from the Python
installation managed by your operating system and makes the relationship
between ``python`` and ``pip`` predictable.

.. tab:: Unix/macOS

   .. code-block:: bash

      python3 --version
      python3 -m venv .venv
      source .venv/bin/activate

.. tab:: Windows

   .. code-block:: bat

      py --version
      py -m venv .venv
      .venv\Scripts\activate

After activation, verify that both commands resolve inside the same
environment:

.. code-block:: console

   python --version
   python -m pip --version

Prefer ``python -m pip`` to a bare ``pip`` command in instructions and when
debugging. It explicitly runs ``pip`` with the interpreter selected by
``python`` and avoids accidentally using a ``pip`` executable from another
installation.

Verify the environment
======================

Check which interpreter is active:

.. code-block:: console

   python -c "import sys; print(sys.executable)"

Check where ``pip`` is installed:

.. code-block:: console

   python -m pip --version

The paths reported by these commands should point into the same virtual
environment. You can also confirm where command-line scripts installed by
packages will be placed:

.. code-block:: console

   python -c "import sysconfig; print(sysconfig.get_path('scripts'))"

While the virtual environment is active, that scripts directory should be
available on your ``PATH`` so tools installed into the environment can be
run directly.

Troubleshooting
===============

If ``python`` is not found after activating the environment, deactivate it
and recreate it with the interpreter command that works on your platform
(``python3`` on many Unix-like systems or ``py`` on Windows).

If ``python -m pip --version`` points outside the virtual environment, the
environment is not active or was created incorrectly. Recreate it rather
than modifying the system Python installation.

If a command installed with ``python -m pip install ...`` cannot be found,
make sure the virtual environment is still active and compare the scripts
directory shown above with your ``PATH``.

On Linux and other systems where Python is managed by the operating system,
avoid changing system-managed packages just to satisfy a project dependency.
Use a virtual environment instead.

Next steps
==========

With this baseline in place, continue with
:doc:`installing-using-pip-and-virtual-environments` for package installation
or the :doc:`/tutorials/packaging-projects` tutorial to build and publish a
project.
