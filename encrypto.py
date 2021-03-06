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
import argparse

EXT = ".enc2"


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
        out_filename = in_filename + EXT

    try:
        iv = get_random_bytes(AES.block_size)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        file_size = os.path.getsize(in_filename)
        progress_bar = ProgressBar(file_size)

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
                    progress_bar.update(chunk_size)
                progress_bar.close()
    except FileNotFoundError:
        print("File '" + in_filename + "' not found.")
    except KeyboardInterrupt:
        os.remove(out_filename)
        print('Encryption canceled by user')


def decrypt_file(key, in_filename, console, out_filename=None, chunk_size=24 * 1024):
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
    console : bool
        echo contents to console instead of writing them to a file.
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
            file_size = os.path.getsize(in_filename)
            buffer = bytearray()
            if console:
                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    buffer += decrypter.decrypt(chunk)
                print(buffer.decode("utf-8"))
            else:
                progress_bar = ProgressBar(file_size)
                with open(out_filename, 'wb') as outfile:
                    while True:
                        chunk = infile.read(chunk_size)
                        if len(chunk) == 0:
                            break
                        outfile.write(decrypter.decrypt(chunk))
                        progress_bar.update(chunk_size)
                    progress_bar.close()
                    outfile.truncate(orig_size)
    except FileNotFoundError:
        print("File '" + in_filename + "' not found.")
    except KeyboardInterrupt:
        os.remove(out_filename)
        print("Decryption canceled by user")


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
    password1 = ""
    try:
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
    except KeyboardInterrupt:
        print(sys.argv[0] + ' canceled by user')
        exit(1)

    return hashlib.sha256(password1.encode("utf-8")).digest()


def throw_warning():
    """"""
    print("Warning! Encrypted files should end with '" + EXT + "'")
    yes_no = str(input("Do you wish to continue [Y/n] > ")).strip(' \t\n').lower()
    if yes_no not in ['', 'y', 'yes']:
        print("Operation canceled by user.")
        exit(1)


def process_files(key, mode, path, console):  # todo : support sub-directories too
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
                print("Encrypting " + file + " to " + file + EXT)
                encrypt_file(key, file)
            elif file[-5:] != EXT:
                throw_warning()
                print("Decrypting '" + file + "' to '" + file + "_decrypted_copy'")
                decrypt_file(key, file, console, file + "_decrypted_copy")
            else:
                print("Decrypting '" + file + "' to '" + file[:-5] + "'")
                decrypt_file(key, file, console, file[:-5])
        return

    f = []
    for (dir_path, dir_names, filenames) in walk(path[0]):
        f.extend(filenames)
        if mode == 'd' or mode == 'd+':
            f = [enc_file for enc_file in f if enc_file.endswith(EXT)]
        break

    for file in f:
        # Get file extension
        parts = file.split('.')
        ext = '.' + parts[len(parts) - 1]

        in_file = os.path.join(path[0], file)

        if mode == 'e':
            if ext != EXT:
                print("Encrypting '" + in_file + "' to '" + in_file + EXT + "'")
                encrypt_file(key, in_file)
        elif ext == EXT:
            out_file = os.path.join(path[0], file[:-5])  # For decryption only
            print("Decrypting " + in_file + " to " + out_file)
            decrypt_file(key, in_file, console, out_file)
        else:
            throw_warning()
            print("Decrypting '" + file + "' to '" + file + "_decrypted_copy'")
            decrypt_file(key, in_file, console, in_file + "_decrypted_copy")


class ProgressBar:
    """tqdm wrapper In case module is missing, script execution continues without a progress bar"""
    chunk_enable = 50

    def __init__(self, file_size):
        if file_size > ProgressBar.chunk_enable * 24 * 1024:
            try:
                from tqdm import tqdm
            except ImportError:
                self.progress_bar = None
                return
            self.progress_bar = tqdm(total=file_size, unit_scale=True)
        else:
            self.progress_bar = None

    def update(self, amount):
        if self.progress_bar is not None:
            self.progress_bar.update(amount)

    def close(self):
        if self.progress_bar is not None:
            self.progress_bar.close()
            print()


def process_args(args):
    """
    Processes given arguments.
    Call script -h for argument information.
    :param args: argparse object
    :return: mode, path
    """
    mode = 'e'
    path = ['.']

    if args.decrypt:
        mode = 'd'
    if args.file is not None:
        mode += '+'

    if args.file is None:
        if mode[0] == 'e':
            path[0] = input('Enter a valid folder with files to encrypt > ')
            if path[0].strip(' \t\n') == '':
                path[0] = '.'
            elif os.path.exists(path[0]) is False:
                print("Invalid path: '" + path[0] + "'")
                exit(1)
        else:
            path[0] = input('Enter a valid folder with files to decrypt > ')
            if path[0].strip(' \t\n') == '':
                path[0] = '.'
            elif os.path.exists(path[0]) is False:
                print("Invalid path: '" + path[0] + "'")
                exit(1)
    else:
        path.clear()
        for file in args.file:
            path.append(file)
    return mode, path


def main():
    print("Security: Random IV and sha256 hashed passwords")
    print("Default extension: '" + EXT + "'")

    parser = argparse.ArgumentParser(description="Encrypto arguments")
    parser.add_argument('-e', '--encrypt', action='store_true', help='encrypt a file. (Default option)')
    parser.add_argument('-d', '--decrypt', action='store_true', help='decrypt a file.')
    parser.add_argument('-c', '--console', action='store_true', help='displays decrypted content to console.')
    parser.add_argument('-f', "--file", type=str, nargs='+', help='the file that\'s going to be processed')
    args = parser.parse_args()
    console = args.console

    mode, path = process_args(args)
    key = password_verification(mode)
    try:
        process_files(key, mode, path, console)
    except ValueError:
        if mode == 'd' or mode == 'd+':
            print('Decryption failed....')
        else:
            print('Encryption failed....')


if __name__ == '__main__':
    main()
