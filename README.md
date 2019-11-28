Usage
=

    Usage: python encrypto.py [-d] [<file>...]
    
    -d      decrypt

Setup guide
=

make sure you have **pipenv** or **virtualenv** installed

    $ pip list
    Package          Version
    ---------------- ----------
    ...
    pipenv           2018.11.26
    ...
    virtualenv       16.7.5
    virtualenv-clone 0.5.3
    ...

or just install **pycryptodome=3.9.0**

    $ pip install pycryptodome=3.9.0

Pipenv
-

If you are using pipenv cd into this project directory and:
    
    $ pipenv install
    
To run it:

    $ pipenv run python encrypto.py
    
Virtualenv
-

If you are using virtualenv cd into this project directory and:

    $ source venv/bin/activate
    
To run it:
    
    $ venv/bin/python encrypto.py
    
Reminder: To leave the virtual environment

    $ deactivate
    
Create the venv on each OS:

    $ python -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt
