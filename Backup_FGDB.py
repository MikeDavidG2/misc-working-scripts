#-------------------------------------------------------------------------------
# Name:        Backup_FGDB.py
# Purpose:
"""
To back up a FGDB (FGDB_to_backup) to a folder (backup_folder) with the date
appended to the end of the name of the backup.  Also to delete older backups
if the max_num_backups has been reached in the backup_folder.

NOTE:
  ListWorkspaces creates a list of workspaces in alphabetical order.
  Since this script appends the dates in both a numerical ascending order
  AND an alphabetical ascending order (YYYY_MM_DD),
  listing the workspaces using arcpy.ListWorkspace() gives us a list in order of
  the oldest workspace listed first.  So we can delete the first listed
  workspaces, which are also the oldest workspaces in the backup_folder.

PROCESS:
  1. Set print statements to write to a log file.
  2. Copy FGDB to Backup folder with the current date appended to its name.
  3. Test for and delete the oldest workspaces if there are more workspaces than
     the max_num_backups allows.
"""

# Author:      mgrue
#
# Created:     28/07/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os

arcpy.env.overwriteOutput = True

def main():

    #---------------------------------------------------------------------------
    #                           USER SET VARIABLES
    #---------------------------------------------------------------------------
    # Set paths
    FGDB_to_backup = r"P:\DPW_ScienceAndMonitoring\Scripts\DEV\Data\DPW_Science_and_Monitoring_prod.gdb"
    backup_folder  = r'P:\DPW_ScienceAndMonitoring\Scripts\DEV\Data\Backups'
    log_file        = r'P:\DPW_ScienceAndMonitoring\Scripts\DEV\Data\Logs\Backup_FGDB'

    # Set number of backups allowed to exist in 'backup_folder'
    max_num_backups = 2

    # 'True' means the print statement will write to a log file
    run_Write_Print_To_Log = True

    #---------------------------------------------------------------------------
    #                           SCRIPT SET VARIABLES
    #---------------------------------------------------------------------------
    success = True

    #---------------------------------------------------------------------------
    #                               START SCRIPT
    #---------------------------------------------------------------------------
    print 'Starting Backup_FGDB.py\n'

    # Set print to logging statement
    if run_Write_Print_To_Log:
        orig_stdout = Write_Print_To_Log(log_file)

    # Copy FGDB to Backup folder
    try:
        date_time = Get_DT_To_Append()  # Returns a string formatted like: 'YYYY_MM_DD__HH_MM_SS'
        date      = date_time.split('__')[0]  # Get only the 'YYYY_MM_DD' portion
        out_FGDB  = os.path.join(backup_folder, 'DPW_Sci_and_Mon_prod_BAK__{}.gdb'.format(date))
        print 'Copying FGDB: "{}"\n          To: "{}"\n'.format(FGDB_to_backup, out_FGDB)
        arcpy.Copy_management(FGDB_to_backup, out_FGDB)
    except Exception as e:
        print '*** ERROR with Copy FGDB to Backup fooder ***'
        print str(e)
        success = False

    # Test to determine how many backups need to be deleted
    arcpy.env.workspace = backup_folder
    workspaces = arcpy.ListWorkspaces('', 'FileGDB')
    print 'There are {} existing workspaces, {} are allowed.'.format(len(workspaces), max_num_backups)

    # Delete workspaces if needed
    if len(workspaces) <= max_num_backups:  # Then no backups need to be deleted
        num_wkspaces_to_del = 0
        print '  No need to delete any workspaces.'

    else:  # Then delete the correct number of backups
        num_wkspaces_to_del = len(workspaces)-max_num_backups

        print '  Deleting {} workspace(s):'.format(str(num_wkspaces_to_del))

        index = 0
        while index < num_wkspaces_to_del:  # Delete the first x number of workspaces
            try:
                print '    Deleting "{}"'.format(workspaces[index])
                arcpy.Delete_management(workspaces[index])
            except Exception as e:
                print '*** ERROR with Deleting ***'
                print str(e)
                success = False
            index += 1

    # Return sys.stdout back to its original setting and end of script reporting
    if (run_Write_Print_To_Log):
        try:
            # Footer for log file
            finish_time_str = [datetime.datetime.now().strftime('%m/%d/%Y  %I:%M:%S %p')][0]
            print '\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            print '                    {}'.format(finish_time_str)
            print '              Finished DPW_Update_sde_load.py'
            print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

            sys.stdout = orig_stdout

        except Exception as e:
            print 'ERROR with end of script reporting'
            print str(e)

    print '\nDone with script.  Success = "{}".'.format(str(success))
    print '  Please find log file location above for more info.'

#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                           START DEFINING FUNCTIONS
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION Write_Print_To_Log()
def Write_Print_To_Log(log_file):
    """
    PARAMETERS:
      log_file (str): Path to log file.  The part after the last "\" will be the
        name of the .log file after the date, time, and ".log" is appended to it.

    RETURNS:
      orig_stdout (os object): The original stdout is saved in this variable so
        that the script can access it and return stdout back to its orig settings.

    FUNCTION:
      To turn all the 'print' statements into a log-writing object.  A new log
        file will be created based on log_file with the date, time, ".log"
        appended to it.  And any print statements after the command
        "sys.stdout = write_to_log" will be written to this log.
      It is a good idea to use the returned orig_stdout variable to return sys.stdout
        back to its original setting.
      NOTE: This function needs the function Get_DT_To_Append() to run

    """
    print 'Starting Write_Print_To_Log()...'

    # Get the original sys.stdout so it can be returned to normal at the
    #    end of the script.
    orig_stdout = sys.stdout

    # Get DateTime to append
    dt_to_append = Get_DT_To_Append()

    # Create the log file with the datetime appended to the file name
    log_file_date = '{}_{}.log'.format(log_file,dt_to_append)
    write_to_log = open(log_file_date, 'w')

    # Make the 'print' statement write to the log file
    print '  Setting "print" command to write to a log file found at:\n    {}'.format(log_file_date)
    sys.stdout = write_to_log

    # Header for log file
    start_time = datetime.datetime.now()
    start_time_str = [start_time.strftime('%m/%d/%Y  %I:%M:%S %p')][0]
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print '                  {}'.format(start_time_str)
    print '                  START Backup_FGDB.py'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n'

    return orig_stdout

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION Get_dt_to_append
def Get_DT_To_Append():
    """
    PARAMETERS:
      none

    RETURNS:
      dt_to_append (str): Which is in the format 'YYYY_M_D__H_M_S'

    FUNCTION:
      To get a formatted datetime string that can be used to append to files
      to keep them unique.
    """
    print '  Starting Get_DT_To_Append()...'

    start_time = datetime.datetime.now()

    date = start_time.strftime('%Y_%m_%d')
    time = start_time.strftime('%H_%M_%S')

    dt_to_append = '%s__%s' % (date, time)

    print '    DateTime to append: "{}"'.format(dt_to_append)

    print '  Finished Get_DT_To_Append()\n'
    return dt_to_append

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
