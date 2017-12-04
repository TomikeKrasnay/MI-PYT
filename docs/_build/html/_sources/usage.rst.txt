Usage
======

.. _PythonAnywhere: https://www.pythonanywhere.com/

Now that you are all set up, you're ready to use **labelord**! Here's the list of all command line interface commands you can use. All of the commands can be used this way:

.. code:: python

    labelord [COMMAND] [OPTIONS] [ARGUMENTS]

If you wish to list all of the available options and commands in your command line interface, just type 

.. code:: python

	labelord

or

.. code:: python

	labelord --help

.. click:: labelord.cli:list_repos
   :prog: list_repos
   :show-nested:

.. click:: labelord.cli:list_labels
   :prog: list_labels
   :show-nested:

.. note::  **REPOSLUG** argument is name of the repository, from which you wish to list the labels.

.. click:: labelord.cli:run
   :prog: run
   :show-nested:

.. note::  You can choose from two **MODE** arguments: UPDATE or REPLACE (depends on action you want to perform).

Run also provides an output to your command line interface, in form of summary with number of repositories updated. In **verbose** mode, every single action is printed, in **quite** mode nothing is printed at all. **Verbose** mode output comes with a few tags:

  - **[ADD]**: label was added,
  - **[UPD]**: label was updated,
  - **[DEL]**: label was deleted,
  - **[DRY]**: action was performed in dry mode,
  - **[LBL]**: comes together with [ERR], when there's error reading label,
  - **[SUC]**: action went successfully,
  - **[ERR]**: an error occurred while perfoming the action.

.. click:: labelord.web:run_server
   :prog: run_server
   :show-nested:

.. note::  If no options are given, the server will run on localhost with port 5000. If you wish to deploy your application to server, you can use for example PythonAnywhere_.

If you wish, you can proceed to the `Examples <examples.html#section>`__ or the full `API documentation <labelord.html#section>`__.