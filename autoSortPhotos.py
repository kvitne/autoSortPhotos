# Python 3.5
# 2016.02.29
# Scans and organizes photos by date taken. Uses dictionaries.

import datetime
import os
import shutil
import sys

import exifread

# Always include \\ at the end of the path
scanFolder = ""
newRootFolder = ""


# Easy to change between copy or moving files. Just switch shutil.copy to shutil.move
def copy_or_move(src, dst):
    shutil.move(src, dst)


# Scans folder and all sub-folders. Returns all absolute file paths, NOT
# directories, as list
def absolute_file_paths(inFolder):
    listFiles = {}
    notImage = []
    movieFiles = {}
    olyRawList = {}
    suffixes = ('.jpg', '.cr2')
    exifCantRead = ('.orf')
    movies = ('.mov', '.avi', '.3gp')
    counting = 0
    for dirpath, _, filenames in os.walk(inFolder):
        for f in filenames:
            filePath = os.path.abspath(os.path.join(dirpath, f))
            filePathLower = filePath.lower()
            if filePathLower.endswith(suffixes):
                listFiles[filePath] = '1111.11.11'
                print (counting, end=" ", flush=True)
                counting += 1
            elif filePathLower.endswith(exifCantRead):
                olyRawList[filePath] = '1112.11.11'
            elif filePathLower.endswith(movies):
                movieFiles[filePath] = '1113.11.11'
            else:
                notImage.append(filePath)
    print ('\nNumber of other files: ' + str(len(notImage)))
    print ('Number of image-files: ' + str(len(listFiles)))
    print ('Number of Olympus RAW-files: ' + str(len(olyRawList)))
    print ('Number of movie-files: ' + str(len(movieFiles)))
    return (listFiles, movieFiles, olyRawList)


# Takes list of dates, formatted as YYYY MM DD, returns list of new
# paths NewRoot/YYYY/YYYY.MM.DD
def new_filepaths_list(datesList):
    listfullNewPaths = []
    if isinstance(datesList, list):
        print('Start creating filepaths from list.')
        for date in datesList:
            yearsCheck = date[:-6]
            fullPath = os.path.join(newRootFolder, yearsCheck, date)
            listfullNewPaths.append(fullPath)
        print('Finish creating filepaths from list.')
    elif isinstance(datesList, dict):
        print('Start creating filepaths from dictionary.')
        for filePath, date in datesList.items():
            yearsCheck = date[:-6]
            fullPath = os.path.join(newRootFolder, yearsCheck, date)
            listfullNewPaths.append(fullPath)
        print('Finish creating filepaths from dictionary.')
    return listfullNewPaths


def movies():
    movieLastModi = get_date_taken('lastModified', listMovies)
    movNewPaths = new_filepaths_list(movieLastModi)
    print('Start copying movies')
    for index, item in enumerate(listMovies):
        fileName = os.path.basename(item)
        if os.path.exists(movNewPaths[index]):
            duplicate_check(item, movNewPaths[index], 'no', index)
        else:
            duplicate_check(item, newRootFolder, 'yes', index)
    print ('Movie-copying done.')


# Reads exif, gets date taken, removes time of day, stores in a list. Or
# gets date last modified.
# whereToGetDate-argument must be 'exif' or 'lastModified'
def get_date_taken(whereToGetDate, filesToCheck):
    dictTest = filesToCheck
    counting = len(filesToCheck)
    if whereToGetDate == 'exif':
        for filePath, date in dictTest.items():
            print (counting, end=" ", flush=True)
            counting -= 1
            x = open(filePath, 'rb')
            tags = exifread.process_file(x, details=False,
                                         stop_tag='DateTimeOriginal')
            if len(tags) < 6:
                print('''No recoverable exif-info in file.
                    Given 1111.11.11 as date.''')
            else:
                for tag in tags.keys():
                    if tag == "EXIF DateTimeOriginal":
                        withoutTime = str(tags[tag])[:-9]
                        periodNotColon = withoutTime.replace(':', '.')
                        dictTest[filePath] = periodNotColon
        print('')
    elif whereToGetDate == 'lastModified':
        print('Begins fetching date last modified:')
        for filePath, date in dictTest.items():
            print (counting, end=" ", flush=True)
            counting -= 1
            mtime = os.path.getmtime(filePath)
            y = str(datetime.date.fromtimestamp(mtime))
            z = y.replace('-', '.')
            dictTest[filePath] = z
        print('')
    else:
        sys.exit("Error: whereToGetDate-argument must be 'exif' or 'lastModified'")
    return dictTest


# Creates folders from list of paths, dictionary or a single path-string.
# Does not overwrite existing dirs.
def create_folder(listOfFolders):
    folders = listOfFolders
    # Checks if argument given is a string or list
    if isinstance(folders, str):
        # ONLY WORKS IN PYTHON 3.4+ . Makes directory if it does not exist
        os.makedirs(folders, exist_ok=True)
    elif isinstance(folders, dict):
        print('Start creating folders from dictionary.')
        for filePath, date in folders.items():
            os.makedirs(filePath, exist_ok=True)
        print('Finish creating folders from dictionary.')
    elif isinstance(folders, list):
        print('Start creating folders from list.')
        for x in folders:
            os.makedirs(x, exist_ok=True)
        print('Finish creating folders from list.')
    else:
        sys.exit('Wrong input-type in argument to create_folder')


# Copy all files to respective date-folders. Consider copies
def image_files():
    exifDates = get_date_taken('exif', listFilePaths)
    partPath = new_filepaths_list(exifDates)
    create_folder(partPath)
    counter = 0
    duplicateCounter = 0
    print('Start copying image-files')
    for index, item in enumerate(listFilePaths):
        dstFolder = partPath[index]
        duplicate_check(item, dstFolder, 'no', index)
    print('Finish copying image-files')
    print('Start copying olympus raw-files')
    for index, x in enumerate(olympusRaw):
        fileName = os.path.basename(x)
        searchFor = str(fileName[:-4]) + '.jpg'
        foundTargetFold = str(find_first_result(
            searchFor, newRootFolder)) + '\\'
        if len(foundTargetFold) > 7:
            duplicate_check(x, foundTargetFold, 'no', index)
        else:
            duplicate_check(x, newRootFolder, 'yes', index)
    print ('Image-copying done.')


# Search given paths and returns path of first match
def find_first_result(name, path):
    for root, dirs, files in os.walk(path):
        # Makes sure capitalization doesn't matter
        if str.lower(name) in [x.lower() for x in files]:
            return root


def duplicate_check(fileToCheck, targetFolder, unknown, index=""):
    if unknown != 'yes' and unknown != 'no':
        print('Error: Unknown must have value yes or no')
    fileName = os.path.basename(fileToCheck)
    fileNameNoExt = fileName[:-4]
    extension = fileName[-4:].lower()
    extUpperNoDot = extension[-3:].upper()
    copyTo = targetFolder + fileName
    dupliNewFileName = fileNameNoExt + '_kopi_' + str(index) + extension
    duplicatePath = targetFolder + dupliNewFileName

    # Files I can get the date taken from
    if extension == '.jpg' or extension == '.cr2':
        if not os.path.exists(copyTo):
            copy_or_move(fileToCheck, copyTo)
        else:
            copy_or_move(fileToCheck, duplicatePath)
    else:  # Other files. Unknown files always put in newRootFolder
        if unknown == 'no':
            if not os.path.exists(copyTo):
                copy_or_move(fileToCheck, copyTo)
            else:
                copy_or_move(fileToCheck, duplicatePath)
        elif unknown == 'yes':
            UnknownFolder = os.path.join(newRootFolder, 'Unknown' + extUpperNoDot)
            create_folder(UnknownFolder)
            copyTo = UnknownFolder + fileName
            if not os.path.exists(copyTo):
                copy_or_move(fileToCheck, copyTo)
            else:
                duplicatePath = UnknownFolder + dupliNewFileName
                copy_or_move(fileToCheck, duplicatePath)


listFilePaths, listMovies, olympusRaw = absolute_file_paths(scanFolder)
image_files()
movies()
