.. toctree::
  :maxdepth: 1

Installing, Upgrading or Removing
=================================

Linux
------
For removal and upgrading consult your package manager manual

Ubuntu 20.10
^^^^^^^^^^^^
.. code-block:: bash

  sudo add-apt-repository ppa:jacotsu/polibeepsync
  sudo apt update
  sudo apt install python3-polibeepsync

Arch
^^^^
.. code-block:: bash

  yay -S polibeepsync


Upgrading
^^^^^^^^^

If you installed poliBeePsync directly, open a terminal, write the following
code and press ``Enter``

.. code-block:: bash

    pip3 install --upgrade poliBeePsync

If you used a virtual environment, before issuing the command, remember to
activate the virtual environment

.. code-block:: bash

    cd ~/polibeepsync-venv
    source bin/activate


Database deletion
^^^^^^^^^^^^^^^^^

.. note::

    This operation is safe and will only delete the internal database and **NOT** the already downloaded files.
    But keep in mind that the files will be **REDOWNLOADED** so any changes to them will be **LOST**.

Open a terminal and type the following command

.. code:: bash

    rm ~/.local/share/poliBeePsync/pbs.data


Removing
^^^^^^^^^^^^^

Uninstall poliBeePsync by writing this code in a terminal

.. code-block:: bash

    pip3 uninstall poliBeePsync

When it asks for confirmation, type ``y`` and press ``Enter`` again.

Removing leftover data
^^^^^^^^^^^^^^^^^^^^^^^
Remove ``~/.config/poliBeePsync`` and ``~/.local/share/poliBeePsync``

.. code-block:: bash

    rm -r ~/.config/poliBeePsync
    rm -r ~/.local/share/poliBeePsync



Windows
--------
Upgrading or installing
^^^^^^^^^^^^^^^^^^^^^^^
Download the exe file from the `latest release <https://github.com/Jacotsu/polibeepsync/releases/latest>`_
and open the downloaded file.


Removing
^^^^^^^^^^^^^

Start > Search > polibeepsync > right click > uninstall

Removing leftover data
^^^^^^^^^^^^^^^^^^^^^^^
The next step is removing the folders in which settings and data are saved.
Remove the following folder ``C:\Users\%USERNAME%\AppData\Local\poliBeePsync\``.

Database deletion
^^^^^^^^^^^^^^^^^

.. note::

    This operation is safe and will only delete the internal database and **NOT** the already downloaded files.
    But keep in mind that the files will be **REDOWNLOADED** so any changes to them will be **LOST**.

Remove the following file ``C:\Users\%USERNAME%\AppData\Local\poliBeePsync\poliBeePsync\pbs.data``


Start the application automatically at boot (Windows)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Right click on the shortcut and select ``copy``.
Open the ``run`` program (you can find it by typing ``run`` after pressing
the "Windows" key), write

.. code-block:: bash

	%AppData%

and then click ``Ok``. In the opened folder, go to ``Microsoft\Windows\Start Menu\Programs\Startup``
and choose ``paste shortcut``. The next time you boot, the program will
start automatically.

Mac Os
-------
The App has been tested and built for Mac Os Big Sur, if the app doesn't work
try to install it through the direct method.

Installing
^^^^^^^^^^^^
Download the .app.zip file from the `latest release <https://github.com/Jacotsu/polibeepsync/releases/latest>`_ and then
then drag it from the Downloads to Applications, `CTRL+Right click` polibeepsync's icon and click `open`.

.. image:: _static/img/mac_installing.png
	:alt: Mac installing.

.. image:: _static/img/mac_installed.png
	:alt: Mac installed.


Removing
^^^^^^^^
Drag the app file from the Applications directory to the bin

.. image:: _static/img/mac_uninstall.png
  :alt: Mac uninstall.

Removing leftover data
^^^^^^^^^^^^^^^^^^^^^^^
Open a terminal and type the following command

.. code:: bash

    rm -rf /Users/$USER/Library/Application Support/poliBeePsync

Database deletion
^^^^^^^^^^^^^^^^^

.. note::

    This operation is safe and will only delete the internal database and **NOT** the already downloaded files.
    But keep in mind that the files will be **REDOWNLOADED** so any changes to them will be **LOST**.

Open a terminal and type the following command

.. code:: bash

    rm /Users/$USER/Library/Application Support/poliBeePsync/pbs.data


Direct installation
-------------------
.. warning::
  Only use the direct installation if you want to hack on polibeepsync or be on the bleeding edge

In a terminal issue the command

.. code-block:: bash

    pip3 install --user poliBeePsync

Once it has finished, you can start the application with the command
``polibeepsync-gui``.

Installation inside a virtual environment
-----------------------------------------
.. warning::
  Only use the virtual env installation if you want to hack on polibeepsync or be on the bleeding edge

1. Create a virtual environment.
    Open a terminal and type
    ::

      sudo pip3 install virtualenv
      virtualenv polibeepsync-venv
      source polibeepsync-venv/bin/activate

    You can choose the name of folder, I chose ``polibeepsync-venv``.

2. Install the program.
    Open a terminal and write
    ::

        pip3 install poliBeePsync

    Press ``Enter`` to confirm and wait.

Once it has finished, you can start the application with the command
``polibeepsync-gui`` if the virtual environment is active (this is done with
the third command shown in point 1).

You can automate this by creating a shell script with the following content

.. code-block:: bash

    cd ~/polibeepsync-venv
    source bin/activate
    polibeepsync-gui &

I recommend adding a custom menu entry to the application menu of your
Desktop Environment.
As an icon, you can use `this one <https://github.com/Jacotsu/polibeepsync/blob/master/icons/polibeepsync.svg>`_.
In this case, you would create an entry for the shell script.


