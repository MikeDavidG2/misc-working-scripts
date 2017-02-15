#-------------------------------------------------------------------------------
# Name:        Open_Files.py
# Purpose:
""" This script allows you to open all of the files in the 'folder_path_to_files'
variable that satisfy the 'file_search_variable'.

'open_files' if set to 'False' will allow you to test which files would be
  opened if you ran the script.

'pause' allows you to change how long the script will wait until it tries
  to open another

'max_files_to_process' allows you to dictate how many files the script will try
  to open.  Just in case too many files are going to try to be opened.
"""
#
# Author:      mgrue
#
# Created:     17/11/2016
# Copyright:   (c) mgrue 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, glob, time

#-------------------------------------------------------------------------------
#                               Variables
#-------------------------------------------------------------------------------
#What folder contains the files you want to open
folder_path_to_files = r'P:\mscp_north\20160502_conservation_analysis\maps'
folder_path_to_files = raw_input('Which folder has the files you want to process? ')

#What file do you want to open.  Use * for a wildcard.
file_search_variable = '*.mxd'
file_search_variable = raw_input('What do you want your search parameters to be? ')

#How long (in seconds) should the script wait before opening the next file?
pause = 10

#Maximum number of files to process (you can set the limit of files this script
# will process here.
max_files_to_process = 16
#-------------------------------------------------------------------------------
#                              FUNCTIONS
#-------------------------------------------------------------------------------
def main():
    print 'Starting Open_Files.py\n'
    print 'The files that will be processed are:'

    #---------------------------------------------------------------------------
    # Let the user know how many files will be processed with the current settings
    total_files_to_process = 0
    for filename in glob.glob(os.path.join(folder_path_to_files, file_search_variable)):
        print '    %s' % filename
        total_files_to_process += 1
    print '\nThere are: %s files to process.\n' % total_files_to_process


    #---------------------------------------------------------------------------
    # If there are more files to process than are allowed,
    # Let the user know that there are too many files
    if total_files_to_process > max_files_to_process:
        print """There are more files to process than are set for the
"max_files_to_process" variable.  Please change this variable if you
need to process all of these files."""
    #---------------------------------------------------------------------------
    # If there are no files to process let the user know
    elif total_files_to_process == 0:
        print """ERROR.  There were no files to process.  Please check the
'folder_path_to_files' and the 'file_search_variable'"""

    #---------------------------------------------------------------------------
    # Ask user if they want to process the files that were printed out above.
    else:
        open_files = raw_input('Do you want to process these files? (y/n) ')

    #---------------------------------------------------------------------------
    # If user wants to process files, process files.
    if open_files == 'y':
        index = 1
        for filename in glob.glob(os.path.join(folder_path_to_files, file_search_variable)):
            print 'Opening %s of %s files' % (index, total_files_to_process)
            print 'Opening: %s' % filename
            os.startfile(filename)
            time.sleep(pause)
            index += 1

    else:
        print """Did not process these files."""
#-------------------------------------------------------------------------------
#                                 START MAIN
#-------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


print '\nFINISHED Open_Files.py'