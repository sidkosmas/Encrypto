Usage
=

    Usage: python encrypto.py [-d] [<file>...]
    
    -d      decrypt

Setup guide
=

Script uses `pycryptodome==3.9.0` (encryption/decryption library) 

    $ pip install pycryptodome==3.9.0

and **optionally** `tqdm==4.39.0` (progress bar)

    $ pip install tqdm==4.39.0

To run it:
    
    $ python encrypto.py

Virtualenv
-

To run it:
    
    $ venv/bin/python encrypto.py
    
Create the venv on each OS:

    $ python -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt
    (venv) $ python encrypto.py             #Optional... Test script
    $ deactivate
