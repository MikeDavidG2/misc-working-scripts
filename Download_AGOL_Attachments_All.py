#-------------------------------------------------------------------------------
# Purpose:
"""
To download all the attachments in a Feature Service.  If the attachment already
exists in the Attachment_Folder, the attachment will not be redownloaded.
This script is intended to initially download all the attachments for an
AGOL feature service, then each subsequent run of the script will only download
newly added attachments that haven't already been downloaded.

This script will:
    1) Create and write to a log file.
    2) Get a token that gives permission to view the AGOL data.
    3) Download the attachments.

NOTE: The CreateReplica URL used in this script gets a replica of the full
  database, this means that even if the Feature Service is set to return 1,000
  features, this script should still download attachments from features >1,000.

Set the following variables in the script:
    name_of_script
    attachment_name_prefix
    use_field_to_name_attachment
    email_admin_ls
    cfgFile

Set the following variables in the cfgFile:
    [Download_Info]
    Log_File_Folder=
    Attachment_Folder=
    FS_name=

    [AGOL]
    usr= (for an AGOL account with permission to access the FS_name)
    pwd= (for an AGOL account with permission to access the FS_name)

    [email]
    usr= (for an email account)
    pwd= (for an email account)
"""
#
# Author:      mgrue
#
# Created:     10/13/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# TODO: Update the script Purpose above to be more accurate.

import arcpy, sys, datetime, os, ConfigParser
arcpy.env.overwriteOutput = True

def main():

    #---------------------------------------------------------------------------
    #                     Set Variables that will change
    #---------------------------------------------------------------------------

    # Name of this script
    name_of_script = '<Name_of_Script_Here>.py'

    #---------------------------------------------------------------------------
    #              The below 2 variables help to control the
    #             naming schema for the downloaded attachments

    # Set the prefix of the name of the downloaded attachments
    # For example 'DA_Fire'
    attachment_name_prefix = '<Attachment_Name_Prefix_Here>'

    # Set the field name of the field that should be used for the main name
    # of the downloaded attachment.
    # This is usually a field that stores a unique value
    # like: Report Number, Sample Event ID
    # This is NOT an ESRI generated ID like Global ID
    use_field_to_name_attachment = '<Field_Used_to_Name_Downloaded_Attachment_Here>'

    # Set the Email variables
    ##email_admin_ls = ['michael.grue@sdcounty.ca.gov', 'randy.yakos@sdcounty.ca.gov', 'gary.ross@sdcounty.ca.gov']
    email_admin_ls = ['michael.grue@sdcounty.ca.gov']  # For testing purposes
    #---------------------------------------------------------------------------
    # Set the path prefix depending on if this script is called manually by a
    #  user running a Batch file, or called by a scheduled task on ATLANTIC server,
    #  or run directly through an IDE.
    called_by = arcpy.GetParameterAsText(0)

    if called_by == 'MANUAL':
        path_prefix = 'P:'

    elif called_by == 'SCHEDULED':
        path_prefix = 'P:'

    else:  # If script run directly in an IDE
        path_prefix = 'P:'

    # Full path to a text file that has the username and password of an account
    #  that has access to at least VIEW the FS in AGOL, as well as an email
    #  account that has access to send emails.
    cfgFile     = r"{}\<Path_to_INI_file_here>".format(path_prefix)

    #---------------------------------------------------------------------------
    # Set variables from the cfgFile
    if os.path.isfile(cfgFile):
        config = ConfigParser.ConfigParser()
        config.read(cfgFile)
    else:
        print("*** ERROR! cannot find valid INI file ***\nMake sure a valid INI file exists at:\n\n{}\n".format(cfgFile))
        print 'You may have to change the name/location of the INI file,\nOR change the variable in the script.'
        raw_input('\nPress ENTER to end script...')
        sys.exit()

    # Set the log file paths
    Log_File_Folder = config.get('Download_Info', 'Log_File_Folder')
    log_file = r'{}\{}'.format(Log_File_Folder, name_of_script.split('.')[0])

    # Set the data paths
    Attachment_Folder = config.get('Download_Info', 'Attachment_Folder')

    # Get the Feature Service Name that holds the Attachments
    FS_name       = config.get('Download_Info', 'FS_name')

    # Set the Get Attachments URL
    gaURL  = r'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/{}/FeatureServer/CreateReplica?'.format(FS_name)

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
        try:
            num_downloaded, success = Get_Attachments(token, gaURL, Attachment_Folder, attachment_name_prefix, use_field_to_name_attachment)
        except Exception as e:
            success = False
            print '*** ERROR with Get_Attachments() ***'
            print str(e)

    #---------------------------------------------------------------------------
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
        There were <b>{}</b> downloaded attachments.<br><br>
        The Log file is at:<br> {}<br><br>
        The Attachment folder is at:<br> {}<br><br>
        Attachments are named <i>Site_XX_YYYYMMDD_nnnnnn_pic_X.jpg</i><br>
        Where 'nnnnnn' is a unique ID (frequently HHMMSS, but could be a random unique ID.<br>
        'pic_X' is the name of the field in the database where the picture was stored.""".format(num_downloaded, log_file_date, Attachment_Folder)

    else:
        subj = 'ERROR running {}'.format(name_of_script)
        body = """There was an error with this script.<br>
        Please see the log file for more info.<br>
        The Log file is at:<br> {}<br><br>
        Attachments named Site_XX_YYYYMMDD_nnnnnn_pic_X.jpg<br>
        'nnnnnn' is a unique ID (frequently HHMMSS, but could be a random unique ID depending on the device).<br>
        'pic_X' is the name of the field the picture belongs to.""".format(log_file_date)

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


#TODO: find a way to rotate the images clockwise 90-degrees
def Get_Attachments(token, gaURL, gaFolder, attachment_name_prefix, use_field_to_name_attachment):
    """
    PARAMETERS:
        token (str): The string token obtained in FUNCTION Get_Token().

        gaURL (str): URL of the CreateReplica end point for the AGOL Feature
          Service we want to download attachments.

        gaFolder (str): Full path to the folder that will hold the downloaded
          attachments.

        attachment_name_prefix (str): The prefix that should be added to every
          downloaded attachment.  I.e. 'DA_Fire'

        use_field_to_name_attachment (str): The field name of the field that
          should be used to find a value for the main name of each downloaded
          attachment.
          This is usually a field that stores a unique value like:
            Report Number, Sample Event ID, etc.
          This is NOT an ESRI generated ID like Global ID

    RETURNS:
      number_dl (int): Count of the number of attachments that were downloaded
        during this run of the script.

      success (bool): Flag to verify if this function ran successfully or if
        there were errors.  True if successful, False if there were errros.


    FUNCTION:
      Gets the attachments (images) that are related to the database features and
      stores them as .jpg in a local file inside the gaFolder.

      1) Attachments (images) are obtained by hitting the REST endpoint of the
         feature service (gaURL) and returning a URL that downloads a JSON file
         (which is a replica of the database).
      2) The script then uses that downloaded JSON file to get the URL of the
         each image.
      3) The JSON file is then used to get the unique name/id of the feature
         so that the downloaded attachment can be named appropriately.

      NOTE:
        The naming schema will be:
        <attachment_name_prefix>_<value in use_field_to_name_attachment for the feature linked to the attachment>_<attachment_name_suffix>
    """

    print '--------------------------------------------------------------------'
    print 'Starting Get_Attachments()'

    import time, urllib, urllib2, json, os

    # Flag to control if this entire function ran successfully
    success = True

    # Flag to set if Attachments were downloaded.  Set to 'True' if downloaded
    attachment_dl = False
    number_dl = 0

    # Print the parameters
    print '  gaURL:\n    {}'.format(gaURL)
    print '  gaFolder:\n    {}'.format(gaFolder)

    #---------------------------------------------------------------------------
    # Get a list of all the files that end with '.jpg' in the attachment folder
    # These are the existing attachments, and do not need to be downloaded again
    existing_attachments = filter(lambda x: (os.path.basename(x)).endswith('.jpg'), os.listdir(gaFolder))
    ##print existing_attachments

    #---------------------------------------------------------------------------
    #              Create the replica and get the replica's URL

    # Set the values used to create the replica in a dictionary
    # It is possible that the 'layers' key may need to be changed if the layer
    # in the AGOL Feature Service is not at the default index of 0.
    gaValues = {
    'f' : 'pjson',
    'replicaName' : 'Attachment_Replica',
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
    ##print gaJson
    try:
        replicaUrl = gaJson['URL']
        ##print '  Replica URL:\n    %s' % str(replicaUrl)  # For testing purposes

    # If the key 'URL' doesn't exist in gaJson, print out the error message and
    # provide a few of the most common reasons for this error.
    except KeyError:
        success = False
        print '\n** ERROR!  There was a KeyError. ***'
        print '  Key "URL" not found, error message in gaJson:'
        try:
            print '    {}\n'.format(gaJson['error']['details'][0])
        except:
            print '    No error message in gaJson\n'
        print '    Frequent reasons for a KeyError:'
        print '    1. Sync is not enabled on the Feature Service'
        print '    2. Token doesn\'t have permission to view the data'
        print '    3. The URL is pointing to an old/non-existing Feature Service:'
        print '       Check the name of the FS.'
        print '       For example:\n                 https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/<!NAME_OF_FEATURE_SERVICE_THAT_MAY_BE_INCORRECT!>/FeatureServer/CreateReplica?'
        print '       "gaURL" = {}'.format(gaURL)

    # Set the token into the URL so it can be accessed
    replicaUrl_token = replicaUrl + '?token={}&f=json'.format(token)
    print '  Replica URL with Token:\n    %s' % str(replicaUrl_token)  # For testing purposes

    #---------------------------------------------------------------------------
    #                         Save the JSON file
    # Access the URL and save the file to the current working directory
    # This will be a temporary file and will be deleted
    JsonFileName = 'Temp_Attachment_JSON.json'

    # Save the file
    # NOTE: the file is saved to the 'current working directory' + 'JsonFileName'
    urllib.urlretrieve(replicaUrl_token, JsonFileName)

    # Allow the script to access the saved JSON file
    cwd = os.getcwd()  # Get the current working directory
    jsonFilePath = cwd + '\\' + JsonFileName # Path to the downloaded json file
    ##print '  Temp JSON file saved to: ' + jsonFilePath

    #---------------------------------------------------------------------------
    #                       Save the attachments

    # Make the gaFolder (to hold attachments) if it doesn't exist.
    if not os.path.exists(gaFolder):
        os.makedirs(gaFolder)

    # Open the JSON file
    with open (jsonFilePath) as data_file:
        data = json.load(data_file)

    # Check to make sure that the 'attachments' key exists
    try:
        save_attachments = True
        data['layers'][0]['attachments'][0]
    except KeyError:
        save_attachments = False
        success = False
        print '\n*** ERROR!  There were no attachments downloaded. There was a KeyError: ***'
        print '  Are "Attachments" Enabled in the Feature Service on AGOL?  If not, enable them and run again.\n'
    except IndexError:
        save_attachments = False
        print '\n*** WARNING.  There were no attachments downloaded. There was an IndexError: ***'
        print '  There are no attachments in the database.'
        print '  OK if this is a new database without any attachments.\n'

    if save_attachments == True:
        # Save the attachments
        # Loop through each 'attachment' and get its parentGlobalId so we can name
        #  it based on its corresponding feature
        print '\n  Attempting to save attachments to: {}\n'.format(gaFolder)

        for attachment in data['layers'][0]['attachments']:
            parent_ID = attachment['parentGlobalId']# globalid of the feature that is linked to this attachment

            # Find the field name that stores this attachment
            pic_name  = attachment['name']
            remove_jpg_from_name = pic_name.split('.')[0]  # Strip the '.jpg' from the pic_name
            attachment_name_suffix = remove_jpg_from_name.split('-')[0]  # Get the field name that stores this picture in the AGOL database

            # Now loop through all of the 'features' and break once the
            # attachments 'parentGlobalId' and a features 'globalid' match
            for feature in data['layers'][0]['features']:
                global_ID            = feature['attributes']['globalid']
                attachment_name_main = feature['attributes'][use_field_to_name_attachment]
                if global_ID == parent_ID:
                    break

            # Format the attach_name
            # For example: 'DA_Fire_20180228.123456_pic_A.jpg'
            #               '{pre}  _    {main}     _ {suffix}.jpg'
            attach_name = '{}_{}_{}.jpg'.format(attachment_name_prefix, attachment_name_main, attachment_name_suffix)

            # Save the attachment if it is not already in the attachment folder
            if attach_name not in existing_attachments:
                try:
                    # Get the token to download the attachment
                    gaValues = {'token' : token }
                    gaData = urllib.urlencode(gaValues)

                    # Get the attachment and save as attachPath
                    attachmentUrl = attachment['url']
                    attach_path = os.path.join(gaFolder, attach_name)
                    print '    {} is being downloaded.'.format(attach_name)
                    urllib.urlretrieve(url=attachmentUrl, filename=attach_path,data=gaData)
                    attachment_dl = True
                    number_dl+=1
                except Exception as e:
                    success = False
                    print '\n*** ERROR! There was a problem with downloading {} ***'.format(attach_name)
                    print '{}\n\n'.format(str(e))

            else:
                print '    {} is already in the attachment folder, did not save.'.format(attach_name)

    if (attachment_dl == False):
        print '\n  No attachments saved this run.\n  OK if no new attachments since last script run.'

    print '\n  All attachments can be found at: %s' % gaFolder

    # Delete the JSON file since it is no longer needed.
    ##print '  Deleting JSON file'
    os.remove(jsonFilePath)

    print 'Finished Get_Attachments()\n'

    return number_dl, success

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
