from django.test import TestCase
from rtfapp.managers import FileSystemManager

import os
import zipfile, shutil
from os import path


class FileSystemManagerTests(TestCase):
	""" Test cases for the File System Manager """

	def test_getHomeDir(self):
		""" getHomeDir() should return home dir """
		self.assertEqual(FileSystemManager.getHomeDir(), path.expanduser("~"))

	def test_fromDir_concatenates(self):
		""" fromDir() should concatenate two strings by / """
		self.assertEqual(FileSystemManager.fromDir("a", "b"), "a/b")
		self.assertEqual(FileSystemManager.fromDir("abba", "baab"), "abba/baab")

	def test_fromHomeDir(self):
		""" fromHomeDir() should construct absolute file path from home
			dir for relative filepath """
		self.assertEqual(FileSystemManager.fromHomeDir("abba/ba"), path.expanduser("~") + "/abba/ba")

	def test_deleteExitstingFile(self):
		""" Delete file if it exists"""
		filename = path.expanduser("~") + "/test_saveFile_saveSingleFile.txt"
		overwrite = path.isfile(filename)
		fileContent = "abbababbabababbabasndkanskdaljdlkajslk6dasld"

		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		self.assertEqual(path.isfile(filename), True)

		FileSystemManager.deleteExistingFile(filename);
		self.assertEqual(path.isfile(filename), False);

	def test_fileExists(self):
		filename = path.expanduser("~") + "/test_saveFile_saveSingleFile.txt"
		fileContent = "abbababbabababbabasndkanskdaljdlkajslk6dasld"

		with open(filename, 'w') as writeFile:
			writeFile.write(fileContent)

		self.assertEqual(path.isfile(filename), True)

	def test_dirExists(self):
		dirExists = path.expanduser("~") 
		self.assertEqual(path.isdir(dirExists), True)
		dirNotExists = path.expanduser("~") + "/test_saveFile_saveSingleFile.txt"
		self.assertEqual(path.isdir(dirNotExists), False)

	def test_saveFile_saveSingleFile(self):
		""" Test saving a test file to the home directory """
		filename = path.expanduser("~") + "/test_saveFile_saveSingleFile.txt"
		overwrite = path.isfile(filename)
		fileContent = "abbababbabababbabasndkanskdaljdlkajslk6dasld"

		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		self.assertEqual(path.isfile(filename), True)
		with open(filename, 'r') as openFile:
			self.assertEqual(openFile.read(), fileContent)

		os.remove(filename)

	def test_saveFile_dontOverwriteFile(self):
		""" Test overwrite feature of saving a file, make sure it doesn't allow saving """
		filename = path.expanduser("~") + "/test_saveFile_dontOverwriteFile.txt"
		overwrite = path.isfile(filename)
		fileContent = ";aksd;lmais6l; im;asmipmilasmidaimsd[pasmidiopasndp"
		dontWriteFileContent = "asdalskmdiA>O<:Dsao;dmasidlmaSdnASdnuISudAMDMASdmOASJd"

		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		self.assertEqual(path.isfile(filename), True)
		self.assertEqual(FileSystemManager.saveFile(filename, dontWriteFileContent, overwrite=False), False)
		
		with open(filename, 'r') as openFile:
			self.assertEqual(openFile.read(), fileContent)

		os.remove(filename)


	def test_deleteExistingFile_fileExists(self):
		#make a file
		filename = path.expanduser("~") + "/test_singleFile.txt"
		overwrite = path.isfile(filename)
		fileContent = "hello"

		#save the file
		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		#check that the file exists after it was saved
		self.assertEqual(path.isfile(filename), True)

		#delete the file and check that it doesn't exist anymore
		FileSystemManager.deleteExistingFile(filename);
		self.assertEqual(FileSystemManager.fileExists(filename), False);

	def test_deleteExistingFile_twoFiles(self):
		#make 2 files, check it deletes the correct file
		filename = path.expanduser("~") + "/test_singleFile.txt"
		overwrite = path.isfile(filename)
		fileContent = "hello"

		filename_1 = path.expanduser("~") + "/test_singleFile1.txt"
		overwrite_1 = path.isfile(filename_1)
		fileContent_1 = "second file hello"

		#save the file
		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		self.assertEqual(FileSystemManager.saveFile(filename_1, fileContent_1, overwrite=overwrite_1), True)
		#check that the file exists after it was saved
		self.assertEqual(path.isfile(filename), True)
		self.assertEqual(path.isfile(filename_1), True)

		FileSystemManager.deleteExistingFile(filename);
		self.assertEqual(FileSystemManager.fileExists(filename), False);
		self.assertEqual(FileSystemManager.fileExists(filename_1), True);

		os.remove(filename_1)

	def test_deleteExistingFile_noFile(self):
		#create a file and don't save it
		filename = path.expanduser("~") + "/test_singleFile.txt"
		overwrite = path.isfile(filename)
		fileContent = "hello"

		self.assertFalse(FileSystemManager.fileExists(filename))
		FileSystemManager.deleteExistingFile(filename);
		self.assertEqual(FileSystemManager.fileExists(filename), False);
		


	def test_unzip_existingDirectory(self):
		test_fileList = []
		filename = path.expanduser("~") + "/files/test_singleFile.txt"
		directory = os.path.dirname(filename)
		if not os.path.exists(directory):
			os.makedirs(directory)

		overwrite = path.isfile(filename)
		fileContent = "hello"

		filename_1 = path.expanduser("~") + "/files/test_singleFile1.txt"
		overwrite_1 = path.isfile(filename_1)
		fileContent_1 = "second file hello"

		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		self.assertEqual(FileSystemManager.saveFile(filename_1, fileContent_1, overwrite=overwrite_1), True)
		
		test_fileList.append(filename)
		test_fileList.append(filename_1)
		zip = shutil.make_archive("zipfile", "zip", directory)

		self.assertTrue(zipfile.is_zipfile(zip))

		fileList = FileSystemManager.unzip(zip, directory)
		self.assertEqual(len(fileList), len(test_fileList))
		self.assertEqual(fileList, test_fileList)

		# shutil.rmtree(directory)
		# os.remove(zip)

	def test_unzip_newDirectory(self):
		test_fileList = []
		filename = path.expanduser("~") + "/files/test_singleFile.txt"
		filename = path.expanduser("~") + "/files/test_singleFile.txt"
		directory = os.path.dirname(filename)
		if not os.path.exists(directory):
			os.makedirs(directory)

		overwrite = path.isfile(filename)
		fileContent = "hello"

		filename_1 = path.expanduser("~") + "/files/test_singleFile1.txt"
		overwrite_1 = path.isfile(filename_1)
		fileContent_1 = "second file hello"

		self.assertEqual(FileSystemManager.saveFile(filename, fileContent, overwrite=overwrite), True)
		self.assertEqual(FileSystemManager.saveFile(filename_1, fileContent_1, overwrite=overwrite_1), True)
		
		test_fileList.append(filename)
		test_fileList.append(filename_1)
		zip = shutil.make_archive("zipfile", "zip", directory)

		shutil.rmtree(directory)

		self.assertTrue(zipfile.is_zipfile(zip))

		fileList = FileSystemManager.unzip(zip, directory)
		self.assertEqual(len(fileList), len(test_fileList))
		self.assertEqual(fileList, test_fileList)

		shutil.rmtree(directory)
		os.remove(zip)

	def test_unzip_file_does_not_exist(self):
		self.assertEqual(len(FileSystemManager.unzip('testfilethatdoesntexist.txt')),0)





