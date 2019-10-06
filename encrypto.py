#!/usr/bin/python3
import os, struct
from Crypto.Cipher import AES	#pycryptodome
from os import walk
import sys

def encrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
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

	chunksize:
		Sets the size of the chunk which the function
		uses to read and encrypt the file. Larger chunk
		sizes can be faster for some files and machines.
		chunksize must be divisible by 16.
	"""
	if not out_filename:
		out_filename = in_filename + '.enc'

	try:
		iv = 16 * b'\x00'  # needs to be encoded, too!
		encryptor = AES.new(key, AES.MODE_CBC, iv)
		filesize = os.path.getsize(in_filename)

		with open(in_filename, 'rb') as infile:
			with open(out_filename, 'wb') as outfile:
				outfile.write(struct.pack('<Q', filesize))
				outfile.write(iv)

				while True:
					chunk = infile.read(chunksize)
					if len(chunk) == 0:
						break
					elif len(chunk) % 16 != 0:
						chunk += b' ' * (16 - len(chunk) % 16)

					outfile.write(encryptor.encrypt(chunk))
	except FileNotFoundError:
		print("File '" + in_filename + "' not found.")

def decrypt_file(key, in_filename, out_filename=None, chunksize=24 * 1024):
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
	chunksize : int
		Sets the size of the chunk which the function
		uses to read and encrypt the file. Larger chunk
		sizes can be faster for some files and machines.
		chunksize must be divisible by 16.
	"""
	if not out_filename:
		out_filename = os.path.splitext(in_filename)[0]

	try:
		with open(in_filename, 'rb') as infile:
			origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
			iv = infile.read(16)
			decryptor = AES.new(key, AES.MODE_CBC, iv)

			with open(out_filename, 'wb') as outfile:
				while True:
					chunk = infile.read(chunksize)
					if len(chunk) == 0:
						break
					outfile.write(decryptor.decrypt(chunk))

				outfile.truncate(origsize)
	except FileNotFoundError:
		print("File '" + in_filename + "' not found.")

def password_verification(mode):
	"""Asks user to enter twice his password
	adds leading zeros and if passwords match
	returns the password. Otherwise application
	is terminated.
	
	Parameters
	----------
	mode : str
		e for dir encryption
		e+ for specific file(s) encryption
		d for dir decryption
		d+ for specific file(s) decryption
	
	Returns
	-------
	str
		the password with leading zeros
	"""
	password1 = str(input("Enter password > "))
	if mode == 'e' or mode == 'e+':
		password2 = str(input("Re-enter password > "))
		if password1 != password2:
			print("Passwords don't match. Terminating...")
			exit(1)

	if len(password1) < 16:
		password1 = password1.zfill(16)
	elif 16 < len(password1) <= 32:
		password1 = password1.zfill(32)
	else:
		print("Maximum key length is 32 characters")
		exit(1)
	return password1
	
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
	mode = 'e'	#default is encryption
	if len(sys.argv) <= 1:
		path[0] = input('Enter a valid folder with files to encrypt > ')
	elif sys.argv[1] == "-d" and len(sys.argv) <= 2:
		path[0] = input('Enter a valid folder with files to decrypt > ')
		mode = 'd'
	else:
		first_file = 1
		if sys.argv[1] == '-d':
			mode = 'd+'
			first_file = 2
		else:
			mode = 'e+'
		path.clear()
		for file_no in range(first_file, len(sys.argv)):
			path.append(sys.argv[file_no])
	return (mode, path)
	
def process_files(key, mode, path):
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
	if(mode == 'd+' or mode == 'e+'):
		for file in path:
			if mode == 'e+':
				print("Encrypting " + file + " to " + file + ".enc")
				encrypt_file(key, file)
			else :
				print("Decrypting " + file + " to " + file[:-4])
				decrypt_file(key, file, file[:-4])
		return
	
	f = []
	for (dirpath, dirnames, filenames) in walk(path[0]):
		f.extend(filenames)
		break

	for file in f:
		parts = file.split('.')
		ext = '.' + parts[len(parts) - 1]
		if mode == 'e':
			if(ext != '.enc'):
				print("Encrypting " + file + " to " + file + ".enc")
				encrypt_file(key, path[0] + file)
		else:
			if(ext == '.enc'):
				print("Decrypting " + file + " to " + file[:-4])
				decrypt_file(key, path[0] + file, path[0] + file[:-4])

def main():
	mode, path = process_args()
	key = bytearray(password_verification(mode), 'utf-8')
	process_files(key, mode, path)

if __name__ == '__main__':
	main()
