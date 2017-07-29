To setup development environment in CWD:

::

    $ # Install whatever packages you don't already have
    $ <package manager> install git python3 python3-virtualenv
    $ git clone https://github.com/SaltyHash/mcdl.git
    $ virtualenv --python=python3 mcdl

To start development:

::

    $ cd .../mcdl/
    $ git pull                           # Pull the latest code
    $ . bin/activate                     # Activate the virtualenv
    $ pip install -r requirements.txt    # Install dependencies, if necessary
    $ python mcdl.py ...                 # Test changes made to mcdl.py

To upload distribution to PyPI:

::

    $ cd .../mcdl/
    $ . bin/activate                     # Activate virtualenv, if necessary
    $ python setup.py sdist              # Create source distribution
    $ python setup.py bdist_wheel        # Create build distribution wheel
    $ twine upload dist/mcdl-X.Y.Z*      # Upload to PyPI
