#!/usr/bin/python3
import os, struct
# noinspection PyPackageRequirements
from Crypto.Cipher import AES  # pycryptodome
from os import walk
import sys
# noinspection PyPackageRequirements
from Crypto.Random import get_random_bytes
import hashlib
import re


def encrypt_file(key, in_filename, out_filename=None, chunk_size=64 * 1024):
    """Encrypts a file using AES (CBC mode) with the given key.

    Parameters
    ----------
    key:
        The encryption key - a string that must be
        either 16, 24 or 32 bytes long. Longer keys
        are more secure.

    in_filename:
        Name of the input file

    out_filename:
        If None, '<in_filename>.enc' will be used.

    chunk_size:
        Sets the size of the chunk which the function
        uses to read and encrypt the file. Larger chunk
        sizes can be faster for some files and machines.
        chunk-size must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    try:
        iv = get_random_bytes(AES.block_size)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        file_size = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', file_size))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))
    except FileNotFoundError:
        print("File '" + in_filename + "' not found.")


def decrypt_file(key, in_filename, out_filename=None, chunk_size=24 * 1024):
    """Decrypts a file using AES (CBC mode) with the
    given key. Parameters are similar to encrypt_file,
    with one difference: out_filename, if not supplied
    will be in_filename without its last extension
    (i.e. if in_filename is 'aaa.zip.enc' then
    out_filename will be 'aaa.zip')

    Parameters
    ----------
    key : bytearray
        The encryption key - a string that must be
        either 16, 24 or 32 bytes long. Longer keys
        are more secure.
    in_filename : str
        the name of the file to be processed.
    out_filename : str
        the output file name
    chunk_size : int
        Sets the size of the chunk which the function
        uses to read and encrypt the file. Larger chunk
        sizes can be faster for some files and machines.
        chunk-size must be divisible by 16.
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    try:
        with open(in_filename, 'rb') as infile:
            orig_size = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decrypter = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    outfile.write(decrypter.decrypt(chunk))

                outfile.truncate(orig_size)
    except FileNotFoundError:
        print("File '" + in_filename + "' not found.")


def password_verification(mode: str) -> bytearray:
    """For encryption asks user twice to type in a password and if
    both are identical will generate an sha256 hash value that will be used
    as a private key for encryption. For decryption hashes the password
    without any validation.

    Parameters
    ----------
    mode : str
        e for dir encryption <br>
        e+ for specific file(s) encryption
        d for dir decryption
        d+ for specific file(s) decryption

    Returns
    -------
    bytearray
        the password with leading zeros
    """
    password1 = str(input("Enter passphrase > "))
    if mode == 'e' or mode == 'e+':
        password2 = str(input("Re-enter passphrase > "))
        if password1 != password2:
            print("Passwords don't match. Terminating...")
            exit(1)

        if not re.match(r'[A-Za-z0-9@#$%^&+=]{5,}', password1):
            print(('\n'
                   'Invalid password format!\n'
                   'At least 5 characters\n'
                   '\n'
                   'Must be restricted to, though does not specifically require any of:\n'
                   'uppercase letters: A-Z\n'
                   'lowercase letters: a-z\n'
                   'numbers: 0-9\n'
                   'any of the special characters: @#$%^&+=\n'))
            exit(1)

    return hashlib.sha256(password1.encode("utf-8")).digest()


def process_args():
    """Arguments define if a directory will be decrypted or encrypted by
    adding or ignoring option '-d'.
    You can also specify files (encrypt/decrypt) by adding relative/full paths
    at the end.

    Returns
    -------
    str
        e for dir encryption
        e+ for specific file(s) encryption
        d for dir decryption
        d+ for specific file(s) decryption
    list
        a list of path files to be encrypted/decrypted.
    """
    path = ['.']
    mode = 'e'  # Default is encryption

    if len(sys.argv) <= 1:
        path[0] = input('Enter a valid folder with files to encrypt > ')
        if path[0].strip(' \t\n') == '':
            path[0] = '.'
        elif os.path.exists(path[0]) is False:
            print("Invalid path: '" + path[0] + "'")
            exit(1)
    elif sys.argv[1] == "-d" and len(sys.argv) <= 2:
        path[0] = input('Enter a valid folder with files to decrypt > ')
        if path[0].strip(' \t\n') == '':
            path[0] = '.'
        elif os.path.exists(path[0]) is False:
            print("Invalid path: '" + path[0] + "'")
            exit(1)
        mode = 'd'
    else:
        first_file = 1  # ignore option '-d'
        if sys.argv[1] == '-d':
            mode = 'd+'
            first_file = 2
        else:
            mode = 'e+'
        path.clear()
        for file_no in range(first_file, len(sys.argv)):
            path.append(sys.argv[file_no])
    return mode, path


def process_files(key, mode, path):  # todo : support sub-directories too
    """Encrypts the whole directory IGNORING SUBDIRECTORIES
    or just specific files defined in cmd argument's list.

    Parameters
    ----------
    key : bytearray
        The encryption key - a string that must be
        either 16, 24 or 32 bytes long. Longer keys
        are more secure.
    mode : str
        e for dir encryption
        e+ for specific file(s) encryption
        d for dir decryption
        d+ for specific file(s) decryption
    path : list
        a list of path files to be encrypted/decrypted.
    """
    if mode == 'd+' or mode == 'e+':
        for file in path:
            if mode == 'e+':
                print("Encrypting " + file + " to " + file + ".enc")
                encrypt_file(key, file)
            else:
                print("Decrypting " + file + " to " + file[:-4])
                decrypt_file(key, file, file[:-4])
        return

    f = []
    for (dir_path, dir_names, filenames) in walk(path[0]):
        f.extend(filenames)
        break

    for file in f:
        # Get file extension
        parts = file.split('.')
        ext = '.' + parts[len(parts) - 1]

        in_file = os.path.join(path[0], file)
        out_file = os.path.join(path[0], file[:-4])  # For decryption only

        if mode == 'e':
            if ext != '.enc':
                print("Encrypting " + in_file + " to " + in_file + ".enc")
                encrypt_file(key, in_file)
        else:
            if ext == '.enc':
                print("Decrypting " + in_file + " to " + out_file)
                decrypt_file(key, in_file, out_file)


def main():
    mode, path = process_args()
    key = password_verification(mode)
    process_files(key, mode, path)


if __name__ == '__main__':
    main()
