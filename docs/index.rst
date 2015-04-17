.. PygInput documentation master file, created by
   sphinx-quickstart on Fri Apr 17 12:39:43 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PygInput's documentation!
====================================

Contents:

.. toctree::
   :maxdepth: 2

PygInput is small `PyGame <http://pygame.org>`_ module for simplifying text input and output. Think of PygInput as (*not so cloe*) drop-in replacement for standart Python's :py:func:`print()` and :py:func:`input()`, which you may use right over the PyGame screen.

Due to its' asynchronic nature, :py:class:`pyginput.Input` requires some usage policy to be enforcesd. See :ref:`api` and :ref:`ex` for more details.

.. _ex:

Examples
========

* The :download:`module itself <../pyginput.py>` has a good :py:func:`__main()` example function.
* Easiest way to use PygInpyt see at :download:`this example <../pyginput_easy.py>`.
* More sophisticated example is :download:`here <../pyginput_example.py>`.

.. _api:

PygInput API
============

.. automodule:: pyginput
   :members:
   :private-members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

