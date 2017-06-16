#-------------------------------------------------------------------------------
# Name:        Sleeper.py
# Purpose:
"""
To cause a 'pause' in a .bat file.  Calling this script at the beginning of a
.bat file will allow the user to pause the running of all subsequent files in
that .bat file until the designated time (the second and third arguments
passed to this script).

There are 3 required arguments and 1 optional:
  path\to\Sleeper.py  <time_of_day>  <additional_day(s)>  {path_to_log_file}

  argv 1: The full path to this script.
          Required

  argv 2: The time (24-hr) the script should be run (format: "4:59" = 4:59am / "23:59" = 11:59pm)
          Required

  argv 3: # of days to add. For example, "Sleeper.py  14:00  1" = (in order to sleep until next 2pm PLUS 1 day)
          Required

  argv 4: The partial path to the log file to be created. The part after the last "\" will be the
          name of the .log file before the dateTime, and ".log" is appended to it.
          For example, "path\to\log\Sleeper_Log" will create a log file:
                       "path\to\log\Sleeper_Log_YYYY_MM_DD__HH_MM_SS.log"
          Optional
"""
#
# Author:      mgrue
#
# Created:     16/06/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import datetime
import sys
import time

def main():

    print 'Starting to run Sleeper.py'

    # If .bat file provided a log file path, turn print statements into logging statements
    if (len(sys.argv) == 4):
        try:
            orig_stdout = Write_Print_To_Log(sys.argv[3])
        except Exception as e:
            print 'Error with Write_Print_To_Log()'
            print str(e)
            time.sleep(60)

    try:
        startTime     = str(sys.argv[1]) + ":00" # add seconds
        startTimeDate = datetime.datetime.strptime(str(datetime.date.today()) + " " + str(startTime),"%Y-%m-%d %H:%M:%S")
        timeNow       = datetime.datetime.now()
        deltaTime     = startTimeDate - timeNow
        deltaSecs     = int(deltaTime.seconds) + (int(sys.argv[2]) * 86400) # deltaSecs + (24 hours * days)

        if (sys.argv[2] != '0'):
            print '  Sleeper.py will finish at the next: {} + {} day(s)'.format(startTime, sys.argv[2])

        else:
            print '  Sleeper.py will finish the next: {}'.format(startTime)

        # Sleep
        time.sleep(deltaSecs)

    except Exception as e:
        print "***ERROR!***"
        print str(e)
        print 'USAGE: Sleeper.py <time_of_day> <additional_day(s)> {path_to_log_file}'
        print 'USAGE: Sleeper.py 14:00 0 (in order to sleep until next 2pm)'
        print 'USAGE: Sleeper.py 14:00 1 (in order to sleep until next 2pm PLUS 1 day)'

    # Return sys.stdout back to its original setting
    if (len(sys.argv) == 4):

        # Footer for log file
        finish_time_str = [datetime.datetime.now().strftime('%m/%d/%Y  %I:%M:%S %p')][0]
        print '\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        print '                    {}'.format(finish_time_str)
        print '              Finished Update_DPW_w_MasterData.py'
        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

        sys.stdout = orig_stdout

        print '\nFinished with Sleeper.py.  Please find log file location above for more info.'

    else:
        print '\nFinished with Sleeper.py'

    time.sleep(5)
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
    ##print 'Starting Write_Print_To_Log()...'

    # Get the original sys.stdout so it can be returned to normal at the
    #    end of the script.
    orig_stdout = sys.stdout

    # Get DateTime to append
    dt_to_append = Get_DT_To_Append()

    # Create the log file with the datetime appended to the file name
    log_file_date = '{}_{}.log'.format(log_file,dt_to_append)
    write_to_log = open(log_file_date, 'w')

    # Make the 'print' statement write to the log file
    print '  Setting "print" command to write to a log file found at:\n  {}'.format(log_file_date)
    sys.stdout = write_to_log

    # Header for log file
    start_time = datetime.datetime.now()
    start_time_str = [start_time.strftime('%m/%d/%Y  %I:%M:%S %p')][0]
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print '                  {}'.format(start_time_str)
    print '                START Sleeper.py'
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
    ##print 'Starting Get_DT_To_Append()...'

    start_time = datetime.datetime.now()

    date = '%s_%s_%s' % (start_time.year, start_time.month, start_time.day)
    time = '%s_%s_%s' % (start_time.hour, start_time.minute, start_time.second)

    dt_to_append = '%s__%s' % (date, time)

    ##print '  DateTime to append: {}'.format(dt_to_append)

    ##print 'Finished Get_DT_To_Append()\n'
    return dt_to_append
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()



