Usage
=
    usage: encrypto.py [-h] [-e] [-d] [-c] [-f FILE [FILE ...]]
    Encrypto arguments
    
    optional arguments:
      -h, --help            show this help message and exit
      -e, --encrypt         encrypt a file. (Default option)
      -d, --decrypt         decrypt a file.
      -c, --console         displays decrypted content to console.
      -f FILE [FILE ...], --file FILE [FILE ...]
                            the file that's going to be processed

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

Create the venv on each OS:

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ venv/bin/pip install -r requirements.txt
    (venv) $ python encrypto.py             #Optional... Test script
    $ deactivate

To run it:
    
    $ venv/bin/python encrypto.py