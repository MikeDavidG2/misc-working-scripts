import os, arcpy, datetime

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                                 FUNCTION Attach_File_to_Email
def Attach_File_To_Email(file_to_attach):
    """
    PARAMETERS:
      file_to_attach (str): Full path to an item to attach to an email.

    RETURNS:
      None

    FUNCTION:
      To attach a file (Excel, Word) to an email.

    NOTE:
      This function is NOT CURRENTLY WORKING.  It simply contains the logic that
      has been used in the past to attach Excel files to emails.
    """
### Import emailing modules
##from email.mime.multipart import MIMEMultipart
##from email.mime.application import MIMEApplication
##from email import encoders
##from email.message import Message
##from email.mime.text import MIMEText

##    msg = MIMEMultipart()
##    msg['Subject']   = subj
##    msg['From']      = "Python Script"
##    msg['To']        = ', '.join(email_list)  # Join each item in list with a ', '
##    msg.attach(MIMEText(body, 'html'))

##    # Set the attachment if needed
##    if (attach_excel_report == True):
##        attachment = MIMEApplication(open(file_to_attach, 'rb').read())
##
##        # Get name for attachment, which should equal the name of the file_to_attach
##        file_name = os.path.split(file_to_attach)[1]
##
##        # Set attachment into msg
##        attachment['Content-Disposition'] = 'attachment; filename = "{}"'.format(file_name)
##        msg.attach(attachment)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                        FUNCTION:  APPEND DATA

def Append_Data(input_item, target, schema_type, field_mapping=None):
    """
    PARAMETERS:
      input_item (str) = Full path to the item to append.
      target (str) = Full path to the item that will be updated.
      schema_type (str) = Controls if a schema test will take place.
      field_mapping {arcpy.FieldMappings obj} = Arcpy Field Mapping object.
        Optional.

    RETURNS:
      None

    FUNCTION:
      To append the data from the input_item to the target using an
      optional arcpy field_mapping object to override the default field mapping.
    """

    print '--------------------------------------------------------------------'
    print 'Appending Data...'
    print '  From: {}'.format(input_item)
    print '  To:   {}'.format(target)

    # If there is a field mapping object, make sure there is no schema test
    if field_mapping <> None:
        schema_type = 'NO_TEST'

    # Process
    arcpy.Append_management(input_item, target, schema_type, field_mapping)

    print 'Successfully appended data.\n'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                                 FUNCTION Copy_Features()
def Copy_Features(in_FC, out_FC):
    """
    PARAMETERS:
      in_FC (str): Full path to an input feature class.
      out_FC (str): Full path to an existing output feature class.

    RETURNS:
      None

    FUNCTION:
      To copy the features from one feature class to another existing
      feature class.
    """

    print 'Starting Copy_Features()...'

    print '  Copying Features from: "{}"'.format(in_FC)
    print '                     To: "{}"'.format(out_FC)

    arcpy.CopyFeatures_management(in_FC, out_FC)

    print 'Finished Copy_Features()\n'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                                 FUNCTION Copy_Rows()
def Copy_Rows(in_table, out_table):
    """
    PARAMETERS:
      in_table (str): Full path to an input table.
      out_table (str): Full path to an existing output table.

    RETURNS:
      None

    FUNCTION:
      To copy the rows from one table to another table.
    """

    print 'Starting Copy_Rows()...'

    print '  Copying Rows from: "{}"'.format(in_table)
    print '                 To: "{}"'.format(out_table)

    arcpy.CopyRows_management(in_table, out_table)

    print 'Finished Copy_Rows()\n'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                           FUNCTION Create_FGDB()
def Create_FGDB(path_name_FGDB, overwrite_if_exists=False):
    """
    PARAMETERS:

    RETURNS:

    FUNCTION:
    """

    print 'Starting Create_FGDB()...'

    path, name = os.path.split(path_name_FGDB)

    #---------------------------------------------------------------------------
    #          Set create_fgdb variable to control if process is run

    # If FGDB doesn't exist, create it
    if not os.path.exists(path_name_FGDB + '.gdb'):
        create_fgdb = True

    # If FGDB does exist...
    else:
        # ... and overwrite_if_exists == True, create it
        if overwrite_if_exists == True:
            create_fgdb = True

        # ... and overwrite_if_exists == False, do not create FGDB
        else:
            create_fgdb = False

    #---------------------------------------------------------------------------
    # Run process if create_fgdb == True
    if create_fgdb == True:
        print '  Creating FGDB: "{}" at: "{}"'.format(name, path)
        arcpy.CreateFileGDB_management(path, name, 'CURRENT')

    else:
        print '  FGDB not created.  Set "overwrite_if_exists" to "True"'

    print 'Finished Create_FGDB()\n'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                                 FUNCTION Delete_Rows()
def Delete_Rows(in_table):
    """
    PARAMETERS:
      in_table (str): Full path to a table.

    RETURNS:
      None

    FUNCTION:
      To delete the rows from one table.
    """

    print 'Starting Delete_Rows()...'

    print '  Deleting Rows from: "{}"'.format(in_table)

    arcpy.DeleteRows_management(in_table, out_table)

    print 'Finished Delete_Rows()\n'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#            FUNCTION: Export DPW_WP_SITES to Survey123's Site_Info csv
def DPW_WP_SITES_To_Survey123_csv(Sites_Export_To_CSV_tbl, DPW_WP_SITES, Site_Info):
    """
    NOTE: This function is from DPW_Science_and_Monitoring.py, but is no longer
    being used in that script.

    PARAMETERS:

    RETURNS:

    FUNCTION:
    """
    print '--------------------------------------------------------------------'
    print 'Exporting Sites Data to the Survey123 CSV...'

    # Sites_Export_To_CSV is a table that has the same schema the CSV needs in
    # order to work with Survey123.

    #---------------------------------------------------------------------------
    #               Delete rows in Sites_Export_To_CSV FGDB table

    print '  Deleting Rows in: {}'.format(Sites_Export_To_CSV_tbl)

    arcpy.DeleteRows_management(Sites_Export_To_CSV_tbl)

    #---------------------------------------------------------------------------
    #         Export prod DPW_WP_SITES to a working table in the working_FGDB

    working_FGDB = os.path.split(Sites_Export_To_CSV_tbl)[0]  # Get the working FGDB path
    DPW_WP_SITES_tbl = 'D_SITES_exported_tbl'
    DPW_WP_SITES_tbl_path = working_FGDB + '\\' + DPW_WP_SITES_tbl

    print '  Exporting DPW_WP_SITES to a working table:'
    print '    From: {}'.format(DPW_WP_SITES)
    print '    To:   {}'.format(DPW_WP_SITES_tbl_path)

    arcpy.TableToTable_conversion(DPW_WP_SITES, working_FGDB, DPW_WP_SITES_tbl)

    #---------------------------------------------------------------------------
    #            Append DPW_WP_SITES_tbl to the Sites_Export_To_CSV table

    inputs = working_FGDB + '\\' + DPW_WP_SITES_tbl

    print '  Appending {}'.format(DPW_WP_SITES_tbl)
    print '    From: {}'.format(inputs)
    print '    To:   {}'.format(Sites_Export_To_CSV_tbl)

    arcpy.Append_management(inputs, Sites_Export_To_CSV_tbl, 'TEST')

    #---------------------------------------------------------------------------
    #                         Field Calculations
    # Some field calculations have to be performed on the Sites_Export_To_CSV_tbl
    # in order that the comma and quote sensitive Survey123 app can read it correctly

    # Do a search for ',' and replace with a ' ' to make sure no commas get into
    #  the CSV file in the Loc_Desc field
    field = 'Loc_Desc'
    expression = '!Loc_Desc!.replace(",", " ")'
    expression_type = "PYTHON_9.3"

    print '  Calculating field: {}, so that it equals: {}'.format(field, expression)

    arcpy.CalculateField_management(Sites_Export_To_CSV_tbl, field, expression, expression_type)

    # Do a search for a quote (") and replace with an 'in.' to make sure no quotes get into
    #  the CSV file in the Loc_Desc field
    ##print '  Replacing \" with an \'in.\' in Loc_Desc field'
    field = 'Loc_Desc'
    expression = "!Loc_Desc!.replace('\"', 'in.')"
    expression_type = "PYTHON_9.3"

    print '  Calculating field: {}, so that it equals: {}'.format(field, expression)

    arcpy.CalculateField_management(Sites_Export_To_CSV_tbl, field, expression, expression_type)

    #---------------------------------------------------------------------------
    #                      Export to CSV and clean up files.

    out_path = os.path.split(Site_Info)[0]  # Get the Path
    out_name = os.path.split(Site_Info)[1]  # Get the file name

    print '  Exporting to CSV'
    print '    From: {}'.format(Sites_Export_To_CSV_tbl)
    print '    To:   {}'.format(Site_Info)

    arcpy.TableToTable_conversion(Sites_Export_To_CSV_tbl, out_path, out_name)

    # Delete the extra files that are not needed that are created by the above export
    print '  Deleting extra files auto-generated by export process.'
    schema_file = out_path + '\\schema.ini'
    xml_file = out_path + '\\Site_Info.txt.xml'
    if os.path.exists(schema_file):
        os.remove(schema_file)
    if os.path.exists(xml_file):
        os.remove(xml_file)

    print 'Successfully exported DPW_WP_SITES to Survey123 CSV\n'

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

    print 'Starting Email_W_Body()'

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

    print 'Successfully emailed results.'


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

    print 'Starting Email()'

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

    print 'Sent email with subject "{}"'.format(email_subject)
    print 'To: {}'.format(email_recipients_str)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                       FUNCTION Excel_To_Table()
def Excel_To_Table(input_excel_file, out_table, sheet):
    """
    PARAMETERS:
        input_excel_file (str): The full path to the Excel file to import.

        out_table (str): The full path to the FGDB and NAME of the table in the FGDB.

        sheet (str): The name of the sheet to import.

    RETURNS:
        none

    FUNCTION:
        To import an Excel sheet into a FGDB.
    """

    print 'Starting Excel_To_Table()...'

    print '  Importing Excel file: {}\{}\n  To: {}'.format(input_excel_file, sheet, out_table)

    # Perform conversion
    arcpy.ExcelToTable_conversion(input_excel_file, out_table, sheet)

    print 'Finished Excel_To_Table()\n'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION:   Export to Excel
def Export_To_Excel(wkg_folder, wkg_FGDB, table_to_export, export_folder, dt_to_append, report_TMDL_csv):
    """
    NOTE: This function is from DPW_Science_and_Monitoring.py, but is no longer
    being used in that script.

    PARAMETERS:

    RETURNS:

    FUNCTION:
      Exports the production DPW_WP_FIELD_DATA table to a working table, deletes the
      unneeded fields in the working table and then exports that table to excel.
      Essentially creating a 'Report' in Excel based on the where_clause.
    """
    print '--------------------------------------------------------------------'
    print 'Exporting to Excel...'


    #---------------------------------------------------------------------------
    #            Export table_to_export to wkg_FGDB to delete fields
    out_path     = wkg_folder + '\\' + wkg_FGDB
    out_name     = 'Report__Bacteria_TMDL_Outfall'
    where_clause = "Project = 'Bacteria TMDL Outfalls'"

    wkg_table = out_path + '\\' + out_name
    print '  Exporting table to table:'
    print '    From:  {}'.format(table_to_export)
    print '    To:    {}'.format(wkg_table)
    print '    Where: {}'.format(where_clause)

    arcpy.TableToTable_conversion(table_to_export, out_path, out_name, where_clause)


    #---------------------------------------------------------------------------
    #              Delete fields that are not needed/wanted in report

    with open (report_TMDL_csv) as csv_file:
        readCSV = csv.reader(csv_file, delimiter = ',')

        fields_to_delete = []

        row_num = 0
        for row in readCSV:
            if row_num > 1:
                f_to_delete = row[0]

                fields_to_delete.append(f_to_delete)
            row_num += 1

    num_deletes = len(fields_to_delete)

    print '  There are {} fields to delete:'.format(num_deletes)

    # If there is at least one field to delete, delete it
    if num_deletes > 0:
        f_counter = 0
        while f_counter < num_deletes:
            drop_field = fields_to_delete[f_counter]
            ##print '    Deleting field: %s...' % drop_field

            arcpy.DeleteField_management(wkg_table, drop_field)

            f_counter += 1
    print '  Fields deleted.'

    #---------------------------------------------------------------------------
    #                            Export table to Excel

    # Make the export file if it doesn't exist
    if not os.path.exists(export_folder):
        os.mkdir(export_folder)

    export_file = export_folder + '\\Bacteria_TMDL_Report_{}.xls'.format(dt_to_append)

    print '  Exporting table to Excel...'
    print '    From: ' + wkg_table
    print '    To :  ' + export_file

    # Process
    arcpy.TableToExcel_conversion(wkg_table, export_file, 'ALIAS')

    print 'Successfully exported database to Excel.\n'

    return export_file

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                             FUNCTION Get_AGOL_Data_All()
def Get_AGOL_Data_All(AGOL_fields, token, FS_url, index_of_layer, wkg_folder, wkg_FGDB, orig_FC):
    """
    PARAMETERS:
      AGOL_fields (str) = The fields we want to have the server return from our query.
        use the string ('*') to return all fields.
      token (str) = The token obtained by the Get_Token() which gives access to
        AGOL databases that we have permission to access.
      FS_url (str) = The URL address for the feature service.
        Should be the service URL on AGOL (up to the '/FeatureServer' part).
      index_of_layer (int)= The index of the specific layer in the FS to download.
        i.e. 0 if it is the first layer in the FS, 1 if it is the second layer, etc.
      wkg_folder (str) = Full path to the folder that contains the FGDB that you
        want to download the data into.  FGDB must already exist.
      wkg_FGDB (str) = Name of the working FGDB in the wkg_folder.
      orig_FC (str) = The name of the FC that will be created to hold the data
        downloaded by this function.  This FC gets overwritten every time the
        script is run.

    RETURNS:
      None

    FUNCTION:
      To download ALL data from a layer in a FS on AGOL, using OBJECTIDs.
      This function, establishs a connection to the
      data, finds out the number of features, gets the highest and lowest OBJECTIDs,
      and the maxRecordCount returned by the server, and then loops through the
      AGOL data and downloads it to the FGDB.  The first time the data is d/l by
      the script it will create a FC.  Any subsequent loops will download the
      next set of data and then append the data to the first FC.  This looping
      will happen until all the data has been downloaded and appended to the one
      FC created in the first loop.

    NOTE:
      Need to have obtained a token from the Get_Token() function.
      Need to have an existing FGDB to download data into.
    """
    print '--------------------------------------------------------------------'
    print 'Starting Get_AGOL_Data_All()'

    # Set URLs
    query_url = FS_url + '/{}/query'.format(index_of_layer)
    print '  Downloading all data found at: {}/{}\n'.format(FS_url, index_of_layer)

    #---------------------------------------------------------------------------
    #        Get the number of records are in the Feature Service layer

    # This query returns ALL the OBJECTIDs that are in a FS regardless of the
    #   'max records returned' setting
    query = "?where=1=1&returnIdsOnly=true&f=json&token={}".format(token)
    obj_count_URL = query_url + query
    ##print obj_count_URL  # For testing purposes
    response = urllib2.urlopen(obj_count_URL)  # Send the query to the web
    obj_count_json = json.load(response)  # Store the response as a json object
    try:
        object_ids = obj_count_json['objectIds']
    except:
        print 'ERROR!'
        print obj_count_json['error']['message']
    num_object_ids = len(object_ids)
    print '  Number of records in FS layer: {}'.format(num_object_ids)

    #---------------------------------------------------------------------------
    #                  Get the lowest and highest OBJECTID
    object_ids.sort()
    lowest_obj_id = object_ids[0]
    highest_obj_id = object_ids[num_object_ids-1]
    print '  The lowest OBJECTID is: {}\n  The highest OBJECTID is: {}'.format(\
                                                  lowest_obj_id, highest_obj_id)

    #---------------------------------------------------------------------------
    #               Get the 'maxRecordCount' of the Feature Service
    # 'maxRecordCount' is the number of records the server will return
    # when we make a query on the data.
    query = '?f=json&token={}'.format(token)
    max_count_url = FS_url + query
    ##print max_count_url  # For testing purposes
    response = urllib2.urlopen(max_count_url)
    max_record_count_json = json.load(response)
    max_record_count = max_record_count_json['maxRecordCount']
    print '  The max record count is: {}\n'.format(str(max_record_count))


    #---------------------------------------------------------------------------

    # Set the variables needed in the loop below
    start_OBJECTID = lowest_obj_id  # i.e. 1
    end_OBJECTID   = lowest_obj_id + max_record_count - 1  # i.e. 1000
    last_dl_OBJECTID = 0  # The last downloaded OBJECTID
    first_iteration = True  # Changes to False at the end of the first loop

    while last_dl_OBJECTID <= highest_obj_id:
        where_clause = 'OBJECTID >= {} AND OBJECTID <= {}'.format(start_OBJECTID, end_OBJECTID)

        # Encode the where_clause so it is readable by URL protocol (ie %27 = ' in URL).
        # visit http://meyerweb.com/eric/tools/dencoder to test URL encoding.
        # If you suspect the where clause is causing the problems, uncomment the
        #   below 'where = "1=1"' clause.
        ##where_clause = "1=1"  # For testing purposes
        print '  Getting data where: {}'.format(where_clause)
        where_encoded = urllib.quote(where_clause)
        query = "?where={}&outFields={}&returnGeometry=true&f=json&token={}".format(where_encoded, AGOL_fields, token)
        fsURL = query_url + query

        # Create empty Feature Set object
        fs = arcpy.FeatureSet()

        #---------------------------------------------------------------------------
        #                 Try to load data into Feature Set object
        # This try/except is because the fs.load(fsURL) will fail whenever no data
        # is returned by the query.
        try:
            ##print 'fsURL %s' % fsURL  # For testing purposes
            fs.load(fsURL)
        except:
            print '*** ERROR, data not downloaded ***'

        #-----------------------------------------------------------------------
        # Process d/l data

        if first_iteration == True:  # Then this is the first run and d/l data to the orig_FC
            path = wkg_folder + "\\" + wkg_FGDB + '\\' + orig_FC
        else:
            path = wkg_folder + "\\" + wkg_FGDB + '\\temp_to_append'

        #Copy the features to the FGDB.
        print '    Copying AGOL database features to: %s' % path
        arcpy.CopyFeatures_management(fs,path)

        # If this is a subsequent run then append the newly d/l data to the orig_FC
        if first_iteration == False:
            orig_path = wkg_folder + "\\" + wkg_FGDB + '\\' + orig_FC
            print '    Appending:\n      {}\n      To:\n      {}'.format(path, orig_path)
            arcpy.Append_management(path, orig_path, 'NO_TEST')

            print '    Deleting temp_to_append'
            arcpy.Delete_management(path)

        # Set the last downloaded OBJECTID
        last_dl_OBJECTID = end_OBJECTID

        # Set the starting and ending OBJECTID for the next iteration
        start_OBJECTID = end_OBJECTID + 1
        end_OBJECTID   = start_OBJECTID + max_record_count - 1

        # If we reached this point we have gone through one full iteration
        first_iteration = False
        print ''

    if first_iteration == False:
        print "  Successfully retrieved data.\n"
    else:
        print '  * WARNING, no data was downloaded. *'

    print 'Finished Get_AGOL_Data_All()'

    return

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                             FUNCTION Get_AGOL_Data_Where()
def Get_AGOL_Data_Where(AGOL_fields, token, FS_url, index_of_layer, where_clause, wkg_folder, wkg_FGDB, orig_FC):
    """
    PARAMETERS:
      AGOL_fields (str) = The fields we want to have the server return from our query.
        use the string ('*') to return all fields.
      token (str) = The token obtained by the Get_Token() which gives access to
        AGOL databases that we have permission to access.
      FS_url (str) = The URL address for the feature service.
        Should be the service URL on AGOL (up to the '/FeatureServer' part).
      index_of_layer (int)= The index of the specific layer in the FS to download.
        i.e. 0 if it is the first layer in the FS, 1 if it is the second layer, etc.
      where_clause (str) = The where clause to add to the query to receive a
        subset of the full dataset.
      wkg_folder (str) = Full path to the 'Data' folder that contains the FGDB's,
        Excel files, Logs, and Pictures.
      wkg_FGDB (str) = Name of the working FGDB in the wkgFolder.
      orig_FC (str) = Name of the FC that will hold the original data downloaded
        by this function.  This FC gets overwritten every time the script is run.

    RETURNS:
      None

    FUNCTION:
      Uses a where_clause to download a subset of data from the FS.
      To download data from AGOL.  This function, establishs a connection to the
      data, creates a FGDB (if needed), creates a FC (or overwrites the existing
      one to store the data, and then copies the data from AGOL to the FC.

    NOTE:
      Need to have obtained a token from the Get_Token() function.
    """

    print 'Starting Get_AGOL_Data()'

    # Set URLs
    query_url = FS_url + '/{}/query'.format(index_of_layer)

    # Encode the where_clause so it is readable by URL protocol (ie %27 = ' in URL).
    # visit http://meyerweb.com/eric/tools/dencoder to test URL encoding.
    # If you suspect the where clause is causing the problems, uncomment the
    #   below 'where = "1=1"' clause.
    ##where_clause = "1=1"  # For testing purposes
    print '  Getting data where: {}'.format(where_clause)
    where_encoded = urllib.quote(where_clause)
    query = "?where={}&outFields={}&returnGeometry=true&f=json&token={}".format(where_encoded, AGOL_fields, token)
    fsURL = query_url + query

    # Create empty Feature Set object
    fs = arcpy.FeatureSet()

    #---------------------------------------------------------------------------
    #                 Try to load data into Feature Set object
    # This try/except is because the fs.load(fsURL) will fail whenever no data
    # is returned by the query.
    try:
        ##print 'fsURL %s' % fsURL  # For testing purposes
        fs.load(fsURL)
    except:
        print '  "fs.load(fsURL)" yielded no data at fsURL.'
        print '  Query may not have yielded any records.'
        print '  Could simply mean there was no data satisfied by the query.'
        print '  Or could be another problem with the Get_AGOL_Data() function.'
        print '  Feature Service: %s' % str(fsURL)

        # If no data downloaded, stop the function here
        print '\n  * WARNING, no data downloaded *'
        print 'Finished Get_AGOL_Data()'
        return

    #---------------------------------------------------------------------------
    #             Data was loaded, CONTINUE the downloading process

    #Create working FGDB if it does not already exist. Leave alone if it does...
    FGDB_path = wkg_folder + '\\' + wkg_FGDB
    if not os.path.exists(FGDB_path):
        print '  Creating FGDB: %s at: %s' % (wkg_FGDB, wkg_folder)

        # Process
        arcpy.CreateFileGDB_management(wkg_folder,wkg_FGDB)

    #---------------------------------------------------------------------------
    #Copy the features to the FGDB.
    orig_path = wkg_folder + "\\" + wkg_FGDB + '\\' + orig_FC
    print '  Copying AGOL database features to: %s' % orig_path

    # Process
    arcpy.CopyFeatures_management(fs,orig_path)

    #---------------------------------------------------------------------------
    print "  Successfully retrieved data.\n"
    print 'Finished Get_AGOL_Data()'

    return

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                        FUNCTION Get_Count_Selected()
def Get_Count_Selected(lyr):
    """
    PARAMETERS:
      lyr (lyr): The layer that should have a selection on it that we want to test.

    RETURNS:
      count_selected (int): The number of selected records in the lyr

    FUNCTION:
      To get the count of the number of selected records in the lyr.
    """

    print 'Starting Get_Count()...'

    # See if there are any selected records
    desc = arcpy.Describe(lyr)

    if desc.fidSet: # True if there are selected records
        result = arcpy.GetCount_management(lyr)
        count_selected = int(result.getOutput(0))

    # If there weren't any selected records
    else:
        count_selected = 0

    print '  Count of Selected: {}'.format(str(count_selected))

    print 'Finished Get_Count()\n'

    return count_selected

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                                 FUNCTION Get_Dataset_Type()
def Get_Dataset_Type(in_item):
    """
    PARAMETERS:
      in_item (str): Full path to an item to get its dataset type.

    RETURNS:
      dataset_type (str): The dataset type of the item.  Common results include:
        'FeatureClass'
        'Table'
        'GeometricNetwork'
        'RasterDataset'

    FUNCTION:
      To get the dataset type of the 'in_item' and return a string describing
      the type of dataset.  Used when the main() may want to treat the item
      differently based on the dataset type.

      For example:
        A 'Table' may require an        'arcpy.CopyRows_management()' while,
        A 'FeatureClass' may require an 'arcpy.CopyFeatures_management()'
    """

    print 'Starting Get_Dataset_Type()...'
    print '  Getting Dataset Type of: "{}"'.format(in_item)

    desc = arcpy.Describe(in_item)
    dataset_type = desc.datasetType

    print '    "{}"'.format(dataset_type)
    print 'Finished Get_Dataset_Type\n'

    return dataset_type

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
    print 'Starting Get_DT_To_Append()...'

    start_time = datetime.datetime.now()

    date = start_time.strftime('%Y_%m_%d')
    time = start_time.strftime('%H_%M_%S')

    dt_to_append = '%s__%s' % (date, time)

    print '  DateTime to append: {}'.format(dt_to_append)

    print 'Finished Get_DT_To_Append()\n'
    return dt_to_append

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION: Get_List_Of_Parcels
def Get_List_Of_Parcels(rmaTrack, parcel_fc, roadBufferVal):
    """
    """

    # Make feature layers needed below
    arcpy.MakeFeatureLayer_management(rmaTrack, 'rmaTrackLyr')
    arcpy.MakeFeatureLayer_management(parcel_fc,  'parcel_fcLyr')


    # Create a cursor to loop through all features in rmaTrack
    with arcpy.da.SearchCursor(rmaTrack, ['OBJECTID']) as trackCursor:
        for row in trackCursor:
            where_clause = "OBJECTID = {}".format(str(row[0])) # Select track by OBJECTID
            print 'Selecting where: ' + where_clause
            arcpy.SelectLayerByAttribute_management('rmaTrackLyr', 'NEW_SELECTION', where_clause)

            # Confirm one track was selected
            numfeats = arcpy.GetCount_management("rmaTrackLyr")
            count = int(numfeats.getOutput(0))
            ##print 'Count: ' + str(count)
            if count == 1:

                # Select parcels by location based on the selected track
                arcpy.SelectLayerByLocation_management('parcel_fcLyr', 'WITHIN_A_DISTANCE', 'rmaTrackLyr', roadBufferVal, 'NEW_SELECTION')

                # Confirm at least one parcel was selected
                numfeats = arcpy.GetCount_management("parcel_fcLyr")
                count = numfeats.getOutput(0)
                print 'Number of selected parcels: ' + str(count)
                if count > 0:

                    # Get a list of ALL the PARCELID's of the selected parcels
                    # Use PARCELID so we don't count 'stacked' parcels,
                    # but only parcel footprints.
                    parcel_ids = []
                    with arcpy.da.SearchCursor('parcel_fcLyr', ['PARCELID']) as parcelCursor:
                        for row in parcelCursor:
                            parcel_ids.append(row[0])

                    # Get a list of all the UNIQUE PARCELID's
                    # set() returns a list of only unique values
                    unique_parcel_ids = sorted(set(parcel_ids))
                    num_unique_parcel_ids = len(unique_parcel_ids)
                    print 'Number of PARCELID\'s: {}'.format(str(num_unique_parcel_ids))

                    # Calculate the PARCEL field in rmaTrack as the number of unique parcel ids
                    # Only the selected feature in rmaTrack will have it's field calculated.
                    arcpy.CalculateField_management('rmaTrackLyr', 'PARCELS', num_unique_parcel_ids, 'PYTHON_9.3')



            print ''

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
#                          FUNCTION Join 2 Objects

def Join_2_Objects(target_obj, target_join_field, to_join_obj, to_join_field, join_type):
    """
    PARAMETERS:
      target_obj (str): The full path to the FC or Table that you want to have
        another object join to.

      target_join_field (str): The field name in the target_obj to be used as the
        primary key.

      to_join_obj (str): The full path to the FC or Table that you want to join
        to the target_obj.

      to_join_field (str): The field name in the to_join_obj to be used as the
        foreign key.

      join_type (str): Specifies what will be done with records in the input
        that match a record in the join table. Valid values:
          KEEP_ALL
          KEEP_COMMON

    RETURNS:
      target_obj (lyr): Return the layer/view of the joined object so that
        it can be processed.

    FUNCTION:
      To join two different objects via a primary key field and a foreign key
      field by:
        1) Creating a layer or table view for each object ('target_obj', 'to_join_obj')
        2) Joining the layer(s) / view(s) via the 'target_join_field' and the
           'to_join_field'

    NOTE:
      This function returns a layer/view of the joined object, remember to delete
      the joined object (arcpy.Delete_management(target_obj)) if performing
      multiple joins in one script.
    """

    print '\n    Starting Join_2_Objects()...'

    # Create the layer or view for the target_obj using try/except
    try:
        arcpy.MakeFeatureLayer_management(target_obj, 'target_obj')
        print '      Made FEATURE LAYER for: {}'.format(target_obj)
    except:
        arcpy.MakeTableView_management(target_obj, 'target_obj')
        print '      Made TABLE VIEW for: {}'.format(target_obj)

    # Create the layer or view for the to_join_obj using try/except
    try:
        arcpy.MakeFeatureLayer_management(to_join_obj, 'to_join_obj')
        print '      Made FEATURE LAYER for: {}'.format(to_join_obj)
    except:
        arcpy.MakeTableView_management(to_join_obj, 'to_join_obj')
        print '      Made TABLE VIEW for: {}'.format(to_join_obj)

    # Join the layers
    print '      Joining "{}"\n         With "{}"\n           On "{}"\n         Type "{}"\n'.format(target_obj, to_join_obj, to_join_field, join_type)
    arcpy.AddJoin_management('target_obj', target_join_field, 'to_join_obj', to_join_field, join_type)

    # Print the fields (only really needed during testing)
    ##fields = arcpy.ListFields('target_obj')
    ##print '  Fields in joined layer:'
    ##for field in fields:
    ##    print '    ' + field.name

    print '    Finished Join_2_Objects()\n'

    # Return the layer/view of the joined object so it can be processed
    return 'target_obj'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                    FUNCTION: New Loc and Loc Desc
def New_Loc_LocDesc(wkg_data, DPW_WP_SITES):
    """
    NOTE: This function is from DPW_Science_and_Monitoring.py, but is no longer
    being used in that script.

    PARAMETERS:

    RETURNS:

    FUNCTION:
    """

    print '--------------------------------------------------------------------'
    print 'Getting new Location Descriptions and Locations from:\n  {}\n'.format(wkg_data)

    #---------------------------------------------------------------------------
    #                      Get new Location Descriptions.

    # Create list and add the first item
    New_LocDescs = ['  The following are New Location Description suggested changes (Please edit associated feature class appropriately):']

    # Create a Search cursor and add data to lists
    cursor_fields = ['SampleEventID', 'Creator', 'StationID', 'site_loc_desc_new']
    where = "site_loc_desc_cor = 'No'"
    with arcpy.da.SearchCursor(wkg_data, cursor_fields, where) as cursor:

        for row in cursor:
            New_LocDesc = ('    For SampleEventID: "{}", Monitor: "{}" said the Location Description for StationID: "{}" was innacurate.  Suggested change: "{}"\n'.format(row[0], row[1], row[2], row[3]))
            New_LocDescs.append(New_LocDesc)

    del cursor

    # If there is only the original New_LocDescs string, then there were no new
    # suggested changes to make, replace the original string with below
    if (len(New_LocDescs) == 1):
        New_LocDescs = ['  There were no New Location Description suggested changes.\n']

    for desc in New_LocDescs:
        print desc

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    #                           Set new Locations

    # Create needed lists
    New_Locs = ['  The following are the sites that were relocated in the field (The changes will be automatically made to the DPW_WP_SITES):']
    StationIDs, ShapeXs, ShapeYs, SampEvntIDs, Creators = ([] for i in range(5))

    # Create Search cursor and add data to lists
    cursor_fields = ['StationID', 'Shape@X', 'Shape@Y', 'SampleEventID', 'Creator']
    where = "site_loc_map_cor = 'No'"
    with arcpy.da.SearchCursor(wkg_data, cursor_fields, where) as cursor:

        for row in cursor:
            StationID    = row[0]
            ShapeX       = row[1]
            ShapeY       = row[2]
            SampleEvntID = row[3]
            Creator      = row[4]

            StationIDs.append(StationID)
            ShapeXs.append(ShapeX)
            ShapeYs.append(ShapeY)
            SampEvntIDs.append(SampleEvntID)
            Creators.append(Creator)

            ##print 'StationID: "{}" has an NEW X of: "{}" and a NEW Y of: "{}"'.format(StationID, ShapeX, ShapeY)

            New_Loc = ('    For SampleEventID: "{}", Monitor: "{}" said the Location Description for StationID: "{}" was innacurate.  Site has been moved.\n'.format(SampleEvntID, Creator, StationID))
            New_Locs.append(New_Loc)

    del cursor

   # If there is only the original New_Locs string, then there were no new
   #  locations to move; no need to update the DPW_WP_SITES
    if(len(New_Locs) == 1):
        New_Locs = ['  There were no relocated sites.\n']

    #---------------------------------------------------------------------------
    # Create an Update cursor to update the Shape column in the DPW_WP_SITES
    else:
        list_counter = 0
        cursor_fields = ['StationID', 'Shape@X', 'Shape@Y']
        with arcpy.da.UpdateCursor(DPW_WP_SITES, cursor_fields) as cursor:
            for row in cursor:

                # Only loop as many times as there are StationIDs to update
                if (list_counter < len(StationIDs)):

                    # If StationID in DPW_WP_SITES equals the StationID in the
                    #  StationIDs list, update the geom for that StationID in DPW_WP_SITES
                    if row[0] == StationIDs[list_counter]:
                        ##print '  Updating StationID: {} with new coordinates.'.format(StationIDs[list_counter])

                        # Give Shape@X and Shape@Y their new values
                        row[1] = ShapeXs[list_counter]
                        row[2] = ShapeYs[list_counter]

                        cursor.updateRow(row)

                        list_counter += 1

        del cursor

        #-----------------------------------------------------------------------
        # Calculate X and Y fields in DPW_WP_SITES now that the geometry has been updated

        # Calculate the Long_X field
        field = 'Long_X'
        expression = "!Shape.Centroid.X!"
        expression_type="PYTHON_9.3"
        arcpy.CalculateField_management(DPW_WP_SITES, field, expression, expression_type)

        # Calculate the Lat_Y field now that the geometry has been updated
        field = 'Lat_Y'
        expression = "!Shape.Centroid.Y!"
        expression_type="PYTHON_9.3"
        arcpy.CalculateField_management(DPW_WP_SITES, field, expression, expression_type)

    for Loc in New_Locs:
        print Loc


    print '\nSuccessfully got new Location Descriptions and set New Locations.\n'

    return New_LocDescs, New_Locs

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                       FUNCTION Select_Object()
def Select_Object(path_to_obj, selection_type, where_clause):
    """
    PARAMETERS:
      path_to_obj (str): Full path to the object (Feature Layer or Table) that
        is to be selected.

      selection_type (str): Selection type.  Valid values are:
        NEW_SELECTION
        ADD_TO_SELECTION
        REMOVE_FROM_SELECTION
        SUBSET_SELECTION
        SWITCH_SELECTION
        CLEAR_SELECTION

      where_clause (str): The SQL where clause.

    RETURNS:
      'lyr' (lyr): The layer/view with the selection on it.

    FUNCTION:
      To perform a selection on the object.
    """

    print 'Starting Select_Object()...'

    # Use try/except to handle either object type (Feature Layer / Table)
    try:
        arcpy.MakeFeatureLayer_management(path_to_obj, 'lyr')
    except:
        arcpy.MakeTableView_management(path_to_obj, 'lyr')

    print '  Selecting "lyr" with a selection type: {}, where: "{}"'.format(selection_type, where_clause)
    arcpy.SelectLayerByAttribute_management('lyr', selection_type, where_clause)

    print 'Finished Select_Object()\n'
    return 'lyr'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def Test_Exists(dataset):
    """
    PARAMETERS:
      dataset (str): Full path to a dataset.  May be a FC, Table, etc.

    RETURNS:
      exists (bool): 'True' if the dataset exists, 'False' if not.

    FUNCTION:
      To test if a dataset exists or not.
    """

    print 'Starting Test_Exists()'

    print '  Testing to see if exists: "{}"'.format(dataset)

    # Test to see if 'dataset' exists or not
    if arcpy.Exists(dataset):
        exists = True
    else:
        exists = False

    print '  Dataset Exists = "{}"'.format(exists)

    print 'Finished Test_Exists\n'

    return exists

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          FUNCTION Test_Schema_Lock()
def Test_Schema_Lock(dataset):
    """
    PARAMETERS:
      dataset (str): Full path to a dataset to be tested if there is a schema lock

    RETURNS:
      no_schema_lock (Boolean): "True" or "False" if there is no schema lock

    FUNCTION:
      To perform a test on a dataset and return "True" if there is no schema
      lock, and "False" if a schema lock already exists.
    """

    print 'Starting Test_Schema_Lock()...'

    print '  Testing dataset: {}'.format(dataset)

    no_schema_lock = arcpy.TestSchemaLock(dataset)
    print '  Dataset available to have a schema lock applied to it = "{}"'.format(no_schema_lock)

    print 'Finished Test_Schema_Lock()\n'

    return no_schema_lock

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                         FUNCTION Update_Cursor_Func()
def Update_Cursor_Func(fc_or_table, field_to_update, id_field, where_clause, value):
    """
    PARAMETERS:
      fc_or_table (str): Full path to a Feature Class or Table to be updated.

      field_to_update (str): Name of the field to be updated.

      id_field (str): Name of the field that acts as a record identifier for the
        user.  Not crucial for the function to run, but useful for the user to
        see which record(s) modified by this function.

      where_clause (str): A SQL string used to return only records that satisfy
        this clause.  Examples that can be directly copied and pasted:
          '"LAYER_NAME" = \'ECO_MSCP_CN_NORTH_DRAFT\''
          '"LAYER_NAME" like \'HYD%\''

      value (str/obj/num): Can be a string (if going into a text field)
                               or a datetime object (if going into a date field)
                               or a number (if going into a numerical field)

    RETURNS:
      None

    FUNCTION:
      To update a 'field_to_update' in a 'fc_or_table' with the 'value' supplied
      using a 'where_clause' to refine the rows that will be updated.

    NOTE:
      This function uses the older arcpy.UpdateCursor() function.  While this
      method works without having to start an edit session if updating an SDE
      (unlike the arcpy.da.UpdateCursor which requires an edit session), the
      arcpy.UpdateCursor is slower and older.
      It is at risk to be discontinued at some point in the future.

    CREATED:
      8/8/2017--Mike Grue
    EDITED:
      8/8/2017--Mike Grue
    """

    import arcpy
    print 'Starting Update_Cursor_Func()'

    # Print statements with all the variables
    print '  Updating fc or table  "{}"'.format(fc_or_table)
    print '    Field being updated "{}"'.format(field_to_update)
    print '                  where  {}'.format(where_clause)
    print '             with value "{}"\n'.format(value)

    #---------------------------------------------------------------------------
    try:
        cursor = arcpy.UpdateCursor(fc_or_table, where_clause)
        row = cursor.next()
        while row:
            print '\n----------------------------------------------------------'
            # Get and print the current value
            id_to_print = row.getValue(id_field)
            current_val = row.getValue(field_to_update)
            print '  Current value for "{}" in field "{}" is "{}"'.format(id_to_print, field_to_update, current_val)

            # Set the value and print the new value
            row.setValue(field_to_update, value)
            print '  New value "{}"'.format(row.getValue(field_to_update))

            # Update and move to next row (if there is one)
            cursor.updateRow(row)
            row = cursor.next()

        del cursor  # Delete the cursor in order for the updates to 'save'
    except Exception as e:
        print '*** ERROR with UpdateCursor() ***'
        print str(e)

    print '\nFinished Update_Cursor_Func()'

    return

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                         FUNCTION: Update_Fields()

def Update_Fields(target_obj, join_field, obj_to_join, fields_to_update):
    """
    PARAMETERS:
      target_obj (str): The full path of the FC/Table to be updated.

      join_field (str): The name of the field used to join the two objects.

      obj_to_join (str): The full path of the FC/Table used to update.

      fields_to_update (list): List of the field names that will be updated.
        Field names must match between the target_obj and the obj_to_join

    RETURNS:
      none

    FUNCTION:
      To calculate the fields in 'fields_to_update' list from the obj_to_join
      to the target_obj

    NOTE:
      This Function needs access to Join_2_Objects() function in order to work.
    """

    print 'Starting Update_Fields()...'

    joined_obj = Join_2_Objects(target_obj, join_field, obj_to_join, join_field, 'KEEP_COMMON')

    # Get the basename of the imported table, i.e. "CIP_5YEAR_POLY_2017_5_15__9_38_50"
    # Will be used in 'expression' below
    obj_to_join_name = os.path.basename(obj_to_join)

    # Get the basename of the target_obj i.e. 'CIP_5YEAR_POLY'
    # Will be used in the 'where_clause' and 'SearchCursor' below
    target_obj_name = os.path.basename(target_obj)

    for field in fields_to_update:

        field_to_calc = '{}.{}'.format(target_obj_name, field)
        expression    = '!{}.{}!'.format(obj_to_join_name, field)

        print '  In joined_fc, calculating field: "{}", to equal: "{}"'.format(field_to_calc, expression)
        arcpy.CalculateField_management(joined_obj, field_to_calc, expression, 'PYTHON_9.3')

    # Delete the layer/view between the SDW FC and the imported table so there
    #   is no 'holdover' when creating the next joined layer/view
    print '\n  Deleting layer/view with the join'
    arcpy.Delete_management(joined_obj)

    print 'Finished Updating Fields\n'

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
    print '  Setting "print" command to write to a log file found at:\n  {}'.format(log_file_date)
    sys.stdout = write_to_log

    # Header for log file
    start_time = datetime.datetime.now()
    start_time_str = [start_time.strftime('%m/%d/%Y  %I:%M:%S %p')][0]
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print '                  {}'.format(start_time_str)
    print '             START <name_of_script_here>.py'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n'

    return orig_stdout

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------