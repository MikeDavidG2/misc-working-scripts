#-------------------------------------------------------------------------------
# Purpose:
"""
To backup a directory (folder) along with all the sub directories and files
"""
#
# Author:      mgrue
#
# Created:     10/13/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, arcpy, shutil


def main():

    #---------------------------------------------------------------------------
    #                     Set Variables that will change

    # Name of this script
    name_of_script = 'Backup_Folder'

    # Set the path prefix depending on if this script is called manually by a
    #  user, or called by a scheduled task on ATLANTIC server.
    called_by                 = arcpy.GetParameterAsText(0)
    folder_to_backup          = arcpy.GetParameterAsText(1)
    folder_to_contain_backups = arcpy.GetParameterAsText(2)

    if called_by == 'MANUAL':
        path_prefix = 'U:'

    elif called_by == 'SCHEDULED':
        path_prefix = 'D:\users'

    else:  # If script run directly
        path_prefix = 'U:'

    log_file = r'{}\grue\Scripts\GitHub\Test\Logs'.format(path_prefix)
    cfgFile = r"U:\yakos\hep_A\PROD\Environment_B\Scripts\Source_Code\config_file.ini"  # With email account info

    # Set the variables for backing up the project folder
    days_to_backup = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    number_of_backups_allowed = 5

    # Set the Email variables
    email_admin_ls = ['michael.grue@sdcounty.ca.gov'] #, 'randy.yakos@sdcounty.ca.gov', 'gary.ross@sdcounty.ca.gov']

    #---------------------------------------------------------------------------
    #                Set Variables that will probably not change

    # Flag to control if there is an error
    success = True

    #---------------------------------------------------------------------------
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #---------------------------------------------------------------------------
    #                          Start Calling Functions

    # Turn all 'print' statements into a log-writing object
    if success == True:
        try:
            orig_stdout, log_file_date = Write_Print_To_Log(log_file, name_of_script)
        except Exception as e:
            success = False
            print '*** ERROR with Write_Print_To_Log() ***'
            print str(e)


    # Create a backup of our data
    now = datetime.datetime.now()
    day_of_week = now.strftime('%A')

    if day_of_week in days_to_backup:

        # Set the variables
        name_of_backup = os.path.basename(folder_to_backup)  # Get the name of the folder that is being backed up
        dt_to_append = Get_DT_To_Append()   # Get the current date and time the folder is being backed up
        path_and_name_of_backup = os.path.join(folder_to_contain_backups, name_of_backup + '_' + dt_to_append)

        # Perform the backup
        Copy_Directory(folder_to_backup, folder_to_contain_backups)

    # See if we need to delete any old backups
    # Get a list of all the folders in the folder_to_contiain_backups that
    #   startwith the name_of_backup
    existing_backups = [ name for name in os.listdir(folder_to_contain_backups) if (os.path.isdir(os.path.join(folder_to_contain_backups, name)) and name.startswith(name_of_backup)) ]
    print existing_backups
    print '  Number of existing backups: {}'.format(len(existing_backups))

    if len(existing_backups) > number_of_backups_allowed:
        num_backups_to_del = len(existing_backups) - number_of_backups_allowed
        print '  Too many backups.  Only {} allowed.  Deleting {} backups\n'.format(number_of_backups_allowed, num_backups_to_del)

        count = 0
        while count < num_backups_to_del:
            folder_to_delete = os.path.join(folder_to_contain_backups, existing_backups[count])
            print '  Deleting {}'.format(folder_to_delete)
            shutil.rmtree(folder_to_delete)
            count += 1

    # Footer for log file
    finish_time_str = [datetime.datetime.now().strftime('%m/%d/%Y  %I:%M:%S %p')][0]
    print '\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print '                    {}'.format(finish_time_str)
    print '              Finished {}'.format(name_of_script)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

    # End of script reporting
    print 'Success = {}'.format(success)
    sys.stdout = orig_stdout

    # Email recipients
    if success == True:
        email_subject = 'SUCCESS running {}'.format(name_of_script)
    else:
        email_subject = 'ERROR running {}'.format(name_of_script)

    Email_W_LogFile(email_subject, email_admin_ls, cfgFile, log_file_date)

    if success == True:
        print 'SUCCESSFULLY ran {}'.format(name_of_script)
    else:
        print '*** ERROR with {} ***'.format(name_of_script)
        print 'Please see log file (noted above) for troubleshooting\n'

    if called_by == 'MANUAL':
        raw_input('Press ENTER to continue')

#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------
#                              Define Functions
#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION Write_Print_To_Log()
def Write_Print_To_Log(log_file, name_of_script):
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
    print 'Find log file found at:\n  {}'.format(log_file_date)
    print '\nProcessing...\n'
    sys.stdout = write_to_log

    # Header for log file
    start_time = datetime.datetime.now()
    start_time_str = [start_time.strftime('%m/%d/%Y  %I:%M:%S %p')][0]
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print '                  {}'.format(start_time_str)
    print '             START {}'.format(name_of_script)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n'

    return orig_stdout, log_file_date

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION Get_dt_to_append
def Get_DT_To_Append():
    """
    PARAMETERS:
      none

    RETURNS:
      dt_to_append (str): Which is in the format 'YYYY_MM_DD__HH_MM_SS'

    FUNCTION:
      To get a formatted datetime string that can be used to append to files
      to keep them unique.
    """
    ##print 'Starting Get_DT_To_Append()...'

    start_time = datetime.datetime.now()

    date = start_time.strftime('%Y_%m_%d')
    time = start_time.strftime('%H_%M_%S')

    dt_to_append = '%s__%s' % (date, time)

    ##print '  DateTime to append: {}'.format(dt_to_append)

    ##print 'Finished Get_DT_To_Append()\n'
    return dt_to_append

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def Copy_Directory(src, dest):
    """
    PARAMETERS:
      src (str): Path to a folder that you want to create a copy of (including
        the files and folder structure).
      dest (str): Path to a folder that will contain the copied folder from
        'src' above.

    RETURNS:
      None

    FUNCTION:
      To create a copy of a folder from the 'src' to the 'dest' folder.  The
        The copied folder (along with all the files and folder structure) will
        be copied to the 'dest' folder.  The new folder will be given the name
        of the 'src' folder with the 'YYYY_MM_DD__HH_MM_SS' appended to it.

    NOTE:
      This function assumes that the Get_DT_To_Append() is available to use.
    """

    import errno, shutil
    print '\n------------------------------------------------------------------'
    print 'Starting Copy_Directory()'

    name_of_backup = os.path.basename(src)  # Get the name of the folder that is being backed up
    dt_to_append = Get_DT_To_Append()   # Get the current date and time the folder is being backed up
    path_and_name_of_backup = os.path.join(dest, name_of_backup + '_' + dt_to_append)

    print '  Copying Directory from: "{}"'.format(src)
    print '                      To: "{}"'.format(path_and_name_of_backup)

    try:
        shutil.copytree(src, path_and_name_of_backup, ignore=shutil.ignore_patterns('*.lock'))
        print ' '
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, path_and_name_of_backup)  # Then copy the file
        else:
            print('*** Directory not copied. Error: %s ***' % e)

    print 'Finished Copy_Directory()'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                               Function Email_W_Body()
def Email_W_Body(subj, body, email_list, cfgFile=
    r"P:\DPW_ScienceAndMonitoring\Scripts\DEV\DEV_branch\Control_Files\accounts.txt"):

    """
    PARAMETERS:
      subj (str): Subject of the email
      body (str): Body of the email in HTML.  Can be a simple string, but you
        can use HTML markup like <b>bold</b>, <i>italic</i>, <br>carriage return
        <h1>Header 1</h1>, etc.
      email_list (str): List of strings that contains the email addresses to
        send the email to.
      cfgFile {str}: Path to a config file with username and password.
        The format of the config file should be as below with
        <username> and <password> completed:

          [email]
          usr: <username>
          pwd: <password>

        OPTIONAL. A default will be used if one isn't given.

    RETURNS:
      None

    FUNCTION: To send an email to the listed recipients.
      If you want to provide a log file to include in the body of the email,
      please use function Email_w_LogFile()
    """
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import ConfigParser, smtplib

    print '  Starting Email_W_Body()'
    print '    With Subject: {}'.format(subj)

    # Set the subj, From, To, and body
    msg = MIMEMultipart()
    msg['Subject']   = subj
    msg['From']      = "Python Script"
    msg['To']        = ', '.join(email_list)  # Join each item in list with a ', '
    msg.attach(MIMEText(body, 'html'))

    # Get username and password from cfgFile
    config = ConfigParser.ConfigParser()
    config.read(cfgFile)
    email_usr = config.get('email', 'usr')
    email_pwd = config.get('email', 'pwd')

    # Send the email
    ##print '  Sending the email to:  {}'.format(', '.join(email_list))
    SMTP_obj = smtplib.SMTP('smtp.gmail.com',587)
    SMTP_obj.starttls()
    SMTP_obj.login(email_usr, email_pwd)
    SMTP_obj.sendmail(email_usr, email_list, msg.as_string())
    SMTP_obj.quit()
    time.sleep(2)

    print '  Successfully emailed results.'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                       FUNCTION Email_W_LogFile()
def Email_W_LogFile(email_subject, email_recipients, email_login_info, log_file=None):
    """
    PARAMETERS:
      email_subject (str): The subject line for the email

      email_recipients (list): List (of strings) of email addresses

      email_login_info (str): Path to a config file with username and password.
        The format of the config file should be as below with
        <username> and <password> completed:

          [email]
          usr: <username>
          pwd: <password>


      log_file {str}: Path to a log file to be included in the body of the
        email. Optional.

    RETURNS:
      None

    FUNCTION:
      To send an email to the listed recipients.  May provide a log file to
      include in the body of the email.
    """

    import smtplib, ConfigParser
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    ##print 'Starting Email()'

    # Set log file into body of email if provided
    if log_file != None:
        # Get the log file to add to email body
        fp = open(log_file,"rb")
        msg = MIMEText(fp.read())
        fp.close()
    else:
        msg = MIMEMultipart()

    # Get username and pwd from the config file
    try:
        config = ConfigParser.ConfigParser()
        config.read(email_login_info)
        email_usr = config.get("email","usr")
        email_pwd = config.get("email","pwd")
    except:
        print 'ERROR!  Could not read config file.  May not exist at location, or key may be incorrect.  Email not sent.'
        return

    # Set from and to addresses
    fromaddr = "dplugis@gmail.com"
    toaddr = email_recipients
    email_recipients_str = ', '.join(email_recipients)  # Join each item in list with a ', '

    # Set visible info in email
    msg['Subject'] = email_subject
    msg['From']    = "Python Script"
    msg['To']      = email_recipients_str

    # Email
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(email_usr,email_pwd)
    s.sendmail(fromaddr,toaddr,msg.as_string())
    s.quit()

    print 'Sent email with subject: "{}"'.format(email_subject)
    print 'To: {}\n'.format(email_recipients_str)

    return

#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
