To start development:

::

    $ . bin/activate

To upload distribution to PyPI:

::

    $ python setup.py sdist            # Create source distribution
    $ python setup.py bdist_wheel      # Create build distribution wheel
    $ twine upload dist/mcdl-X.Y.Z*    # Upload to PyPI
