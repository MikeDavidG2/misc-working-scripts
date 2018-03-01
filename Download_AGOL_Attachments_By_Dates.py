#-------------------------------------------------------------------------------
# Purpose:
"""
To download the attachments in a Feature Service
"""
#
# Author:      mgrue
#
# Created:     10/13/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# TODO: Update the script Purpose above to be more accurate.

import arcpy, sys, datetime, os, ConfigParser, urllib, urllib2, json, shutil
arcpy.env.overwriteOutput = True

def main():

    #---------------------------------------------------------------------------
    #                     Set Variables that will change
    #---------------------------------------------------------------------------

    # Name of this script
    name_of_script = 'Download_AGOL_Attachments'

    # Set the path prefix depending on if this script is called manually by a
    #  user, or called by a scheduled task on ATLANTIC server.
    called_by = arcpy.GetParameterAsText(0)

    if called_by == 'MANUAL':
        path_prefix = 'U:'
        get_dates = 'Manually'
        days_to_run = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    elif called_by == 'SCHEDULED':
        path_prefix = 'D:\users'
        get_dates = 'Automatically'
        days_to_run = ['Saturday']  # Only run this script via SCHEDULED task once per week

    else:  # If script run directly
        path_prefix = 'U:'
        get_dates = 'Manually'
        days_to_run = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    #---------------------------------------------------------------------------
    # Full path to a text file that has the username and password of an account
    #  that has access to at least VIEW the FS in AGOL, as well as an email
    #  account that has access to send emails.
    cfgFile     = r"{}\yakos\hep_A\PROD\Environment_B\Scripts_B\Source_Code\config_file.ini".format(path_prefix)
    if os.path.isfile(cfgFile):
        config = ConfigParser.ConfigParser()
        config.read(cfgFile)
    else:
        print("INI file not found. \nMake sure a valid '.ini' file exists at {}.".format(cfgFile))
        sys.exit()

    # Set the log file variables
    log_file = r'{}\yakos\hep_A\PROD\Environment_B\Scripts_B\Logs\{}'.format(path_prefix, name_of_script)

    # Set the data paths
    attachments_folder = r'{}\yakos\hep_A\PROD\Environment_B\Attachments_B'.format(path_prefix)

    # Get list of Feature Service Names and find the FS that has the attachments
    FS_names       = config.get('Download_Info', 'FS_names')
    FS_names_ls    = FS_names.split(', ')
    FS_index_in_ls = 2  # This index is the position of the FS with the attachments in the FS_names_ls list

    # Set the Email variables
    email_admin_ls = ['michael.grue@sdcounty.ca.gov', 'randy.yakos@sdcounty.ca.gov', 'gary.ross@sdcounty.ca.gov']
    ##email_admin_ls = ['michael.grue@sdcounty.ca.gov']  # For testing purposes
    #---------------------------------------------------------------------------
    #                Set Variables that will probably not change

    # Flag to control if there is an error
    success = True

    #---------------------------------------------------------------------------
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #---------------------------------------------------------------------------
    #                          Start Calling Functions

    # See if this program should be run
    now = datetime.datetime.now()
    day_of_week = now.strftime('%A')

    if day_of_week not in days_to_run:
        print 'This script is not programmed to run today.  It runs on:'
        for day in days_to_run:
            print '  {}'.format(day)
        sys.exit(0)

    # Turn all 'print' statements into a log-writing object
    if success == True:
        try:
            orig_stdout, log_file_date = Write_Print_To_Log(log_file, name_of_script)
        except Exception as e:
            success = False
            print '*** ERROR with Write_Print_To_Log() ***'
            print str(e)

    # Get the dates to search from/to
    if get_dates == 'Manually':
        from_date = raw_input('What day do you want to start getting attachments? (YYYY-MM-DD)\n  Attachments from this date will be included in the results.')
        to_date   = raw_input('What day do you want to stop getting attachments? (YYYY-MM-DD)\n  Attachments from this date will NOT be included in the results.')

    if get_dates == 'Automatically':
        now = datetime.datetime.now()
        from_date = (now - datetime.timedelta(days=7)).strftime('%Y-%m-%d') # Grab photos taken one week ago
        to_date   = (now + datetime.timedelta(days=2)).strftime('%Y-%m-%d') # Make sure to grab all of the photos up to the current time (even those submitted late yesterday)

        # If run by scheduled task (i.e. Automatically), create a weekly folder to d/l the attachments into
        attachments_folder = os.path.join(attachments_folder, '{}__{}'.format(from_date, to_date))
        if os.path.exists(attachments_folder):
            shutil.rmtree(attachments_folder)
        os.mkdir(attachments_folder)

    print 'Got Dates: {}'.format(get_dates)
    print 'from_date: {}\n  to_date: {}\n'.format(from_date, to_date)

    # Get a token with permissions to view the data
    if success == True:
        try:
            token = Get_Token(cfgFile)
        except Exception as e:
            success = False
            print '*** ERROR with Get_Token() ***'
            print str(e)

    # Get Attachments
    if success == True:
        # Set the full FS URL. "1vIhDJwtG5eNmiqX" is the CoSD portal server so it shouldn't change much.
        FS_url  = r'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/{}/FeatureServer'.format(FS_names_ls[FS_index_in_ls])
        gaURL = FS_url + '/CreateReplica?'  # Get Attachments URL
        ##print gaURL  # For testing purposes

        num_downloaded = Get_Attachments(token, gaURL, attachments_folder, from_date, to_date)

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
        subj = 'SUCCESS running {}'.format(name_of_script)
        body = """Success<br>
        There were <b>{}</b> downloaded attachments.
        The Log file name is: {}<br><br>
        The Attachment folder is named: {}<br><br>
        Attachments are named <i>Site_XX_YYYYMMDD_nnnnnn_pic_X.jpg</i><br>
        Where 'nnnnnn' is a unique ID (frequently HHMMSS, but could be a random unique ID.<br>
        'pic_X' is the name of the field the picture belongs to.""".format(num_downloaded, os.path.basename(log_file_date), os.path.basename(attachments_folder))

    else:
        subj = 'ERROR running {}'.format(name_of_script)
        body = """There was an error with this script.<br>
        Please see the log file for more info.<br>
        The Log file name is: {}<br><br>
        Attachments named Site_XX_YYYYMMDD_nnnnnn_pic_X.jpg<br>
        'nnnnnn' is a unique ID (frequently HHMMSS, but could be a random unique ID depending on the device).<br>
        'pic_X' is the name of the field the picture belongs to.""".format(os.path.basename(log_file_date))

    Email_W_Body(subj, body, email_admin_ls, cfgFile)

    # End of script reporting
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
#                       FUNCTION:    Get AGOL token
def Get_Token(cfgFile, gtURL="https://www.arcgis.com/sharing/rest/generateToken"):
    """
    PARAMETERS:
      cfgFile (str):
        Path to the .txt file that holds the user name and password of the
        account used to access the data.  This account must be in a group
        that has access to the online database.
        The format of the config file should be as below with
        <username> and <password> completed:

          [AGOL]
          usr: <username>
          pwd: <password>

      gtURL {str}: URL where ArcGIS generates tokens. OPTIONAL.

    VARS:
      token (str):
        a string 'password' from ArcGIS that will allow us to to access the
        online database.

    RETURNS:
      token (str): A long string that acts as an access code to AGOL servers.
        Used in later functions to gain access to our data.

    FUNCTION: Gets a token from AGOL that allows access to the AGOL data.
    """

    print '--------------------------------------------------------------------'
    print "Getting Token..."

    import ConfigParser, urllib, urllib2, json

    # Get the user name and password from the cfgFile
    configRMA = ConfigParser.ConfigParser()
    configRMA.read(cfgFile)
    usr = configRMA.get("AGOL","usr")
    pwd = configRMA.get("AGOL","pwd")

    # Create a dictionary of the user name, password, and 2 other keys
    gtValues = {'username' : usr, 'password' : pwd, 'referer' : 'http://www.arcgis.com', 'f' : 'json' }

    # Encode the dictionary so they are in URL format
    gtData = urllib.urlencode(gtValues)

    # Create a request object with the URL adn the URL formatted dictionary
    gtRequest = urllib2.Request(gtURL,gtData)

    # Store the response to the request
    gtResponse = urllib2.urlopen(gtRequest)

    # Store the response as a json object
    gtJson = json.load(gtResponse)

    # Store the token from the json object
    token = gtJson['token']
    ##print token  # For testing purposes

    print "Successfully retrieved token.\n"

    return token

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                         FUNCTION:   Get Attachments
# Attachments (images) are obtained by hitting the REST endpoint of the feature
# service (gaURL) and returning a URL that downloads a JSON file (which is a
# replica of the database).  The script then uses that downloaded JSON file to
# get the URL of the actual images.  The JSON file is then used to get the
# StationID and SampleEventID of the related feature so they can be used to name
# the downloaded attachment.

#TODO: find a way to rotate the images clockwise 90-degrees
def Get_Attachments(token, gaURL, gaFolder, from_date, to_date):
    """
    PARAMETERS:
        token (str):
            The string token obtained in FUNCTION Get_Token().
        gaURL (str):  URL
        wkgFolder (str):
            The variable set in FUNCTION main() which is a path to our working
            folder.
        dt_to_append (str):
            The date and time string returned by FUNCTION Get_DateAndTime().
        from_date (str):

        to_date (str):

    RETURNS:
        gaFolder (str): Path to the folder to contain the downloaded images

    FUNCTION:
      Gets the attachments (images) that are related to the database features and
      stores them as .jpg in a local file inside the gaFolder.
    """

    print '--------------------------------------------------------------------'
    print 'Getting Attachments...'

    import time
    # Flag to set if Attachments were downloaded.  Set to 'True' if downloaded
    attachment_dl = False
    number_dl = 0
    #---------------------------------------------------------------------------
    #                       Get the attachments url (ga)

    # Set the values in a dictionary
    gaValues = {
    'f' : 'pjson',
    'replicaName' : 'Homeless_Activity_Replica',
    'layers' : '0',
    'geometryType' : 'esriGeometryPoint',
    'transportType' : 'esriTransportTypeUrl',
    'returnAttachments' : 'true',
    'returnAttachmentDatabyURL' : 'false',
    'token' : token
    }

    # Get the Replica URL
    gaData = urllib.urlencode(gaValues)
    gaRequest = urllib2.Request(gaURL, gaData)
    gaResponse = urllib2.urlopen(gaRequest)
    gaJson = json.load(gaResponse)
    replicaUrl = gaJson['URL']
    ##print '  Replica URL: %s' % str(replicaUrl)  # For testing purposes

    # Set the token into the URL so it can be accessed
    replicaUrl_token = replicaUrl + '?token={}&f=json'.format(token)
    print '  Replica URL Token: %s' % str(replicaUrl_token)  # For testing purposes

    #---------------------------------------------------------------------------
    #                         Save the JSON file
    # Access the URL and save the file to the current working directory named
    # 'myLayer.json'.  This will be a temporary file and will be deleted

    JsonFileName = 'Temp_JSON.json'

    # Save the file
    # NOTE: the file is saved to the 'current working directory' + 'JsonFileName'
    urllib.urlretrieve(replicaUrl_token, JsonFileName)

    # Allow the script to access the saved JSON file
    cwd = os.getcwd()  # Get the current working directory
    jsonFilePath = cwd + '\\' + JsonFileName # Path to the downloaded json file
    print '  Temp JSON file saved to: ' + jsonFilePath

    #---------------------------------------------------------------------------
    #                       Save the attachments

    # Make the gaFolder (to hold attachments) if it doesn't exist.
    if not os.path.exists(gaFolder):
        os.makedirs(gaFolder)

    # Open the JSON file
    with open (jsonFilePath) as data_file:
        data = json.load(data_file)

    # Get time objects to compare
    from_date_dtobj = time.strptime(from_date, '%Y-%m-%d')
    to_date_dtobj   = time.strptime(to_date, '%Y-%m-%d')

    # Save the attachments
    # Loop through each 'attachment' and get its parentGlobalId so we can name
    #  it based on its corresponding feature
    print '  Attempting to save attachments to: {}'.format(gaFolder)

    for attachment in data['layers'][0]['attachments']:
        parent_ID = attachment['parentGlobalId']
        pic_name = attachment['name']

        # Now loop through all of the 'features' and break once the corresponding
        #  GlobalId's match
        for feature in data['layers'][0]['features']:
            global_ID     = feature['attributes']['globalid']
            site_number   = feature['attributes']['Site_Number']
            date_of_visit = feature['attributes']['Date_Of_Visit']
            if global_ID == parent_ID:
                break

        # Only Download if the date_of_visit is between the from_date and the to_date
        if time.localtime(date_of_visit/1000) > from_date_dtobj and time.localtime(date_of_visit/1000) < to_date_dtobj:

            # Format the attach_name
            remove_jpg_from_name = pic_name.split('.')[0]  # Strip the '.jpg' from the name
            pic_letter = remove_jpg_from_name.split('-')[0]  # Get the letter of the picture (this letter matches to the Visits database)
            pic_date   = time.strftime('%Y%m%d', time.localtime(date_of_visit/1000))  # Format the date to equal the date of the visit
            pic_time   = remove_jpg_from_name[-6:]  # This may be the time (HHMMSS), or it could be just a unique ID depending on the device taking the pic

            attach_name = 'Site_{}_{}-{}_{}.jpg'.format(site_number, pic_date, pic_time, pic_letter)


            # Get the token to download the attachment
            gaValues = {'token' : token }
            gaData = urllib.urlencode(gaValues)

            # Get the attachment and save as attachPath
            attachmentUrl = attachment['url']
            attach_path = os.path.join(gaFolder, attach_name)
            print '    Saving {}'.format(attach_name)
            urllib.urlretrieve(url=attachmentUrl, filename=attach_path,data=gaData)
            attachment_dl = True
            number_dl+=1

    if (attachment_dl == False):
        print '    No attachments saved this run.  OK if no attachments submitted since last run.'

    print '  All attachments can be found at: %s' % gaFolder

    # Delete the JSON file since it is no longer needed.
    print '  Deleting JSON file'
##    os.remove(jsonFilePath)

    print 'Successfully got attachments.\n'

    return number_dl

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

    print '\n  Starting Email_W_Body()'
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

    print '  Successfully emailed results.\n'

#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
