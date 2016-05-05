# Management system for interacting with the File System
# for storage on the server
import datetime
from datetime import datetime
import os
from os import path
import zipfile


def getHomeDir():
	""" Get the home directory path """
	return path.expanduser("~")

def fromDir(dirpath, filepath):
	""" Concatenate dir to path """
	return dirpath + "/" + filepath

def fromHomeDir(pathFromHome):
	""" Retrieve absolute file path: 
		(home dir) + / + (relative file path) """
	return fromDir(getHomeDir(), pathFromHome)

def deleteExistingFile(filepath):
	""" Delete file if it exists """
	if path.isfile(filepath):
		#print("\tDeleting existing: %s", filepath)
		os.remove(filepath)

def fileExists(filepath):
	""" Does the file exist """
	return path.isfile(filepath)

def dirExists(filepath):
	""" Does the directory exist """
	return path.isdir(filepath)

def saveFile(filepath, fileContent, overwrite=False):
	""" Save file to absolute filepath, overwrite if desired.
		Returns whether or not there was a successful save. """
	# Check conditions for overwrite
	if not overwrite and path.isfile(filepath):
		return False
	elif path.isfile(filepath):
		# print ("\tDeleting existing: %s" % filepath, )
		os.remove(filepath)

	# Create necessary directories
	filedir = os.path.dirname(filepath)
	if not os.path.exists(filedir):
		# print ("\tMaking directories: %s" % filedir, )
		os.makedirs(filedir)
	# Write file
	# print ("\tSaving file: %s" % filepath, )
	with open(filepath, 'w') as writeFile:
		writeFile.write(fileContent)

	# Success
	return True

def unzip(filepath, output_dir=None, overwrite=False):
	""" Unzip files to output dir (default home dir) and return 
		list of successfully extracted files """
	filelist = []
	if not fileExists(filepath):
		# print ("File does not exist")
		return filelist

	# Default home dir
	if output_dir == None:
		output_dir = getHomeDir()

	# Create output dir if needed
	if not path.isdir(output_dir):
		# print ("Making directories: %s" % output_dir, )
		os.makedirs(output_dir)

	with open(filepath, 'rb') as openFile:
		zipped = zipfile.ZipFile(openFile)

		# Iterate through files and extract them
		for filename in zipped.namelist():
			extractedPath = fromDir(output_dir, filename)

			if overwrite:
				deleteExistingFile(extractedPath)

			# print ("\tExtracting: %s" % extractedPath, )
			zipped.extract(filename, output_dir)
			if not dirExists(extractedPath):
				filelist.append(extractedPath)

	return filelist

def zip(files, output_name, output_dir=None, overwrite=False):
	""" Zip a file to output dir (default home dir) and return 
		list of successfully extracted files """
	# Default home dir
	if output_dir == None:
		output_dir = getHomeDir()

	# Create output dir if needed
	if not path.isdir(output_dir):
		# print ("Making directories: %s" % output_dir, )
		os.makedirs(output_dir)

	zipName = fromDir(output_dir, output_name)

	# Check overwrite
	if not overwrite and fileExists(zipName):
		return False

	zf = zipfile.ZipFile(zipName, "w")

	for f in files:
		zf.write(f, os.path.basename(f), zipfile.ZIP_STORED)

	zf.close()
	return True

def findLatestFile(directory, file_extension, timestamp_format):
	""" Find the latest file within the directory with the specified file
		extension, given files with names formatted using the
		specified timestamp format. No files in format will result
		in None.
		File extension should be format: .ext (e.g. .zip)
	"""
	if not dirExists(directory):
		return None

	# Most recent file
	most_recent = None
	most_recent_datetime = None

	for current_file in os.listdir(directory):
		# Check file format
		if current_file.endswith(file_extension):
			try:
				# Parse file format
				current_datetime = datetime.strptime(current_file.replace(file_extension, ""), timestamp_format)

				# Select most recent file (set full path)
				if most_recent_datetime == None or current_datetime > most_recent_datetime:
					most_recent = directory + current_file
					most_recent_datetime = current_datetime
			except ValueError:
				# File not in format
				continue

	return most_recent
