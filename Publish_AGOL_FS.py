# Publish_AGOL_FS.py - update hosted feature services by replacing the .SD file
#   and calling publishing (with overwrite) to update the feature service
# Edits by Mike Grue are noted with <MG MM/DD/YY ... >
# Requires a Configuration settings file (.ini)
# Downloaded the script from:  https://github.com/arcpy/update-hosted-feature-service

import ConfigParser
import ast
import os
import sys
import time

import urllib2
import urllib
import json
import mimetypes
import gzip
from io import BytesIO
import string
import random

from xml.etree import ElementTree as ET
import arcpy
import shutil


#-------------------------------------------------------------------------------
#                             Set Variables <MG 02/12/2018>
#-------------------------------------------------------------------------------

# Name of this script
name_of_script = '<name_of_script_here>.py'

# Name of ini file located in the same location as this script.
cfgFile = r"<ini_file_here>.ini"

if os.path.isfile(cfgFile):
    config = ConfigParser.ConfigParser()
    config.read(cfgFile)
else:
    print("*** ERROR! cannot find valid INI file ***\nMake sure a valid INI file exists at:\n\n{}\n".format(cfgFile))
    print 'You may have to change the name/location of the INI file,\nOR change the variable in the script.'
    raw_input('\nPress ENTER to end script...')
    sys.exit()

# Log file is a concatenation of the config file path to the log folder and the name of the script (w/o the .py)
# The .ini file should have a section named:
#   [Log_File]
#   Log_File_Folder = '<full path to log file folder here>'
log_file = '{}\{}'.format(config.get('Log_File', 'Log_File_Folder'), name_of_script.split('.')[0])

# Permissions
permissions_to_set = "Query"  # <Full permissions = "Query,Create,Update,Delete,Uploads,Editing,Sync">

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                           MG's Functions Below
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
#                           MG's Functions Above
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

class AGOLHandler(object):

    def __init__(self, username, password, serviceName, folderName, proxyDict):

        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': ('updatehostedfeatureservice')
        }
        self.username = username
        self.password = password
        self.base_url = "https://www.arcgis.com/sharing/rest"
        self.proxyDict = proxyDict
        self.serviceName = serviceName
        self.token = self.getToken(username, password)
        self.itemID = self.findItem("Feature Service")
        self.SDitemID = self.findItem("Service Definition")
        self.folderName = folderName
        self.folderID = self.findFolder()

    def getToken(self, username, password, exp=60):

        referer = "http://www.arcgis.com/"
        query_dict = {'username': username,
                      'password': password,
                      'expiration': str(exp),
                      'client': 'referer',
                      'referer': referer,
                      'f': 'json'}

        token_url = '{}/generateToken'.format(self.base_url)

        token_response = self.url_request(token_url, query_dict, 'POST')

        if "token" not in token_response:
            print(token_response['error'])
            sys.exit()
        else:
            return token_response['token']

    def findItem(self, findType):
        """ Find the itemID of whats being updated
        """

        searchURL = self.base_url + "/search"

        query_dict = {'f': 'json',
                      'token': self.token,
                      'q': "title:\"" + self.serviceName + "\"AND owner:\"" +
                      self.username + "\" AND type:\"" + findType + "\""}

        jsonResponse = self.url_request(searchURL, query_dict, 'POST')

        if jsonResponse['total'] == 0:
            print("\nCould not find a service to update. Check the service name in the settings.ini")
            sys.exit()
        else:
            resultList = jsonResponse['results']
            for it in resultList:
                if it["title"] == self.serviceName:
                    print("Found {} : {}").format(findType, it["id"])
                    return it["id"]

    def findFolder(self, folderName=None):
        """ Find the ID of the folder containing the service
        """

        if self.folderName == "None":
            return ""

        findURL = "{}/content/users/{}".format(self.base_url, self.username)

        query_dict = {'f': 'json',
                      'num': 1,
                      'token': self.token}

        jsonResponse = self.url_request(findURL, query_dict, 'POST')

        for folder in jsonResponse['folders']:
            if folder['title'] == self.folderName:
                return folder['id']

        print("\nCould not find the specified folder name provided in the settings.ini")
        print("-- If your content is in the root folder, change the folder name to 'None'")
        sys.exit()

    def upload(self, fileName, tags, description):
        """
         Overwrite the SD on AGOL with the new SD.
         This method uses 3rd party module: requests
        """

        updateURL = '{}/content/users/{}/{}/items/{}/update'.format(self.base_url, self.username,
                                                                    self.folderID, self.SDitemID)

        query_dict = {"filename": fileName,
                      "type": "Service Definition",
                      "title": self.serviceName,
                      "tags": tags,
                      "description": description,
                      "f": "json",
                      'multipart': 'true',
                      "token": self.token}

        details = {'filename': fileName}
        add_item_res = self.url_request(updateURL, query_dict, "POST", "", details)

        try:
            itemPartJSON = self._add_part(fileName, add_item_res['id'], "Service Definition")
        except KeyError as e:
            print 'fileName = {}'.format(fileName)
            print add_item_res['error']['message']
            print str(e)

        if "success" in itemPartJSON:
            itemPartID = itemPartJSON['id']

            commit_response = self.commit(itemPartID)

            # valid states: partial | processing | failed | completed
            status = 'processing'
            while status == 'processing' or status == 'partial':
                status = self.item_status(itemPartID)['status']
                time.sleep(1.5)

            print("Updated SD:   {}".format(itemPartID))
            return True

        else:
            print("\n.sd file not uploaded. Check the errors and try again.\n")
            print(itemPartJSON)
            sys.exit()

    def _add_part(self, file_to_upload, item_id, upload_type=None):
        """ Add the item to the portal in chunks.
        """

        def read_in_chunks(file_object, chunk_size=10000000):
            """Generate file chunks of 10MB"""
            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break
                yield data

        url = '{}/content/users/{}/items/{}/addPart'.format(self.base_url, self.username, item_id)

        with open(file_to_upload, 'rb') as f:
            for part_num, piece in enumerate(read_in_chunks(f), start=1):
                title = os.path.basename(file_to_upload)
                files = {"file": {"filename": file_to_upload, "content": piece}}
                params = {
                    'f': "json",
                    'token': self.token,
                    'partNum': part_num,
                    'title': title,
                    'itemType': 'file',
                    'type': upload_type
                }

                request_data, request_headers = self.multipart_request(params, files)
                resp = self.url_request(url, request_data, "MULTIPART", request_headers)

        return resp

    def item_status(self, item_id, jobId=None):
        """ Gets the status of an item.
        Returns:
            The item's status. (partial | processing | failed | completed)
        """

        url = '{}/content/users/{}/items/{}/status'.format(self.base_url, self.username, item_id)
        parameters = {'token': self.token,
                      'f': 'json'}

        if jobId:
            parameters['jobId'] = jobId

        return self.url_request(url, parameters)

    def commit(self, item_id):
        """ Commits an item that was uploaded as multipart
        """

        url = '{}/content/users/{}/items/{}/commit'.format(self.base_url, self.username, item_id)
        parameters = {'token': self.token,
                      'f': 'json'}

        return self.url_request(url, parameters)

    def publish(self):
        """ Publish the existing SD on AGOL (it will be turned into a Feature Service)
        """

        publishURL = '{}/content/users/{}/publish'.format(self.base_url, self.username)

        query_dict = {'itemID': self.SDitemID,
                      'filetype': 'serviceDefinition',
                      'overwrite': 'true',
                      'f': 'json',
                      'token': self.token}

        jsonResponse = self.url_request(publishURL, query_dict, 'POST')
        try:
            if 'jobId' in jsonResponse['services'][0]:
                jobID = jsonResponse['services'][0]['jobId']

                # valid states: partial | processing | failed | completed
                status = 'processing'
                print("Checking the status of publish..")
                while status == 'processing' or status == 'partial':
                    status = self.item_status(self.SDitemID, jobID)['status']
                    print("  {}".format(status))
                    time.sleep(2)

                if status == 'completed':
                    print("Item finished published")
                    return jsonResponse['services'][0]['serviceItemId']
                if status == 'failed':
                    raise("Status of publishing returned FAILED.")

        except Exception as e:
            print("Problem trying to check publish status. Might be further errors.")
            print("Returned error Python:\n   {}".format(e))
            print("Message from publish call:\n  {}".format(jsonResponse))
            print(" -- quit --")
            sys.exit()


    def enableSharing(self, newItemID, everyone, orgs, groups):
        """ Share an item with everyone, the organization and/or groups
        """

        shareURL = '{}/content/users/{}/{}/items/{}/share'.format(self.base_url, self.username,
                                                                  self.folderID, newItemID)
        print 'shareURL: {}'.format(shareURL)  # <MG 20180212: to see why the share isn't working>
        if groups is None:
            groups = ''

        query_dict = {'f': 'json',
                      'everyone': everyone,
                      'org': orgs,
                      'groups': groups,
                      'token': self.token}

        jsonResponse = self.url_request(shareURL, query_dict, 'POST')

        print("successfully shared...{}...".format(jsonResponse['itemId']))

    def url_request(self, in_url, request_parameters, request_type='GET',
                    additional_headers=None, files=None, repeat=0):
        """
        Make a request to the portal, provided a portal URL
        and request parameters, returns portal response.

        Arguments:
            in_url -- portal url
            request_parameters -- dictionary of request parameters.
            request_type -- HTTP verb (default: GET)
            additional_headers -- any headers to pass along with the request.
            files -- any files to send.
            repeat -- repeat the request up to this number of times.

        Returns:
            dictionary of response from portal instance.
        """

        if request_type == 'GET':
            req = urllib2.Request('?'.join((in_url, urllib.urlencode(request_parameters))))
        elif request_type == 'MULTIPART':
            req = urllib2.Request(in_url, request_parameters)
        else:
            req = urllib2.Request(
                in_url, urllib.urlencode(request_parameters), self.headers)

        if additional_headers:
            for key, value in list(additional_headers.items()):
                req.add_header(key, value)
        req.add_header('Accept-encoding', 'gzip')

        if self.proxyDict:
            p = urllib2.ProxyHandler(self.proxyDict)
            auth = urllib2.HTTPBasicAuthHandler()
            opener = urllib2.build_opener(p, auth, urllib2.HTTPHandler)
            urllib2.install_opener(opener)

        response = urllib2.urlopen(req)

        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            with gzip.GzipFile(fileobj=buf) as gzip_file:
                response_bytes = gzip_file.read()
        else:
            response_bytes = response.read()

        response_text = response_bytes.decode('UTF-8')
        response_json = json.loads(response_text)

        if not response_json or "error" in response_json:
            rerun = False
            if repeat > 0:
                repeat -= 1
                rerun = True

            if rerun:
                time.sleep(2)
                response_json = self.url_request(
                    in_url, request_parameters, request_type,
                    additional_headers, files, repeat)

        return response_json

    def multipart_request(self, params, files):
        """ Uploads files as multipart/form-data. files is a dict and must
            contain the required keys "filename" and "content". The "mimetype"
            value is optional and if not specified will use mimetypes.guess_type
            to determine the type or use type application/octet-stream. params
            is a dict containing the parameters to be passed in the HTTP
            POST request.

            content = open(file_path, "rb").read()
            files = {"file": {"filename": "some_file.sd", "content": content}}
            params = {"f": "json", "token": token, "type": item_type,
                      "title": title, "tags": tags, "description": description}
            data, headers = multipart_request(params, files)
            """
        # Get mix of letters and digits to form boundary.
        letters_digits = "".join(string.digits + string.ascii_letters)
        boundary = "----WebKitFormBoundary{}".format("".join(random.choice(letters_digits) for i in range(16)))
        file_lines = []
        # Parse the params and files dicts to build the multipart request.
        for name, value in params.iteritems():
            file_lines.extend(("--{}".format(boundary),
                               'Content-Disposition: form-data; name="{}"'.format(name),
                               "", str(value)))
        for name, value in files.items():
            if "filename" in value:
                filename = value.get("filename")
            else:
                raise Exception("The filename key is required.")
            if "mimetype" in value:
                mimetype = value.get("mimetype")
            else:
                mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            if "content" in value:
                file_lines.extend(("--{}".format(boundary),
                                   'Content-Disposition: form-data; name="{}"; filename="{}"'.format(name, filename),
                                   "Content-Type: {}".format(mimetype), "",
                                   (value.get("content"))))
            else:
                raise Exception("The content key is required.")
        # Create the end of the form boundary.
        file_lines.extend(("--{}--".format(boundary), ""))

        request_data = "\r\n".join(file_lines)
        request_headers = {"Content-Type": "multipart/form-data; boundary={}".format(boundary),
                           "Content-Length": str(len(request_data))}
        return request_data, request_headers


def makeSD(MXD, serviceName, tempDir, outputSD, maxRecords, tags, summary):
    """ create a draft SD and modify the properties to overwrite an existing FS
    """

    arcpy.env.overwriteOutput = True
    # All paths are built by joining names to the tempPath
    SDdraft = os.path.join(tempDir, "tempdraft.sddraft")
    newSDdraft = os.path.join(tempDir, "updatedDraft.sddraft")

    # Check the MXD for summary and tags, if empty, push them in.
    try:
        mappingMXD = arcpy.mapping.MapDocument(MXD)
        if mappingMXD.tags == "":
            mappingMXD.tags = tags
            mappingMXD.save()
        if mappingMXD.summary == "":
            mappingMXD.summary = summary
            mappingMXD.save()
    except IOError:
        print("IOError on save, do you have the MXD open? Summary/tag info not pushed to MXD, publishing may fail.")

    arcpy.mapping.CreateMapSDDraft(MXD, SDdraft, serviceName, "MY_HOSTED_SERVICES")

    # Read the contents of the original SDDraft into an xml parser
    doc = ET.parse(SDdraft)

    root_elem = doc.getroot()
    if root_elem.tag != "SVCManifest":
        raise ValueError("Root tag is incorrect. Is {} a .sddraft file?".format(SDDraft))

    # The following 6 code pieces modify the SDDraft from a new MapService
    # with caching capabilities to a FeatureService with Query,Create,
    # Update,Delete,Uploads,Editing capabilities as well as the ability
    # to set the max records on the service.
    # The first two lines (commented out) are no longer necessary as the FS
    # is now being deleted and re-published, not truly overwritten as is the
    # case when publishing from Desktop.
    # The last three pieces change Map to Feature Service, disable caching
    # and set appropriate capabilities. You can customize the capabilities by
    # removing items.
    # Note you cannot disable Query from a Feature Service.

    # doc.find("./Type").text = "esriServiceDefinitionType_Replacement"
    # doc.find("./State").text = "esriSDState_Published"

    # Change service type from map service to feature service
    for config in doc.findall("./Configurations/SVCConfiguration/TypeName"):
        if config.text == "MapServer":
            config.text = "FeatureServer"

    # Turn off caching
    for prop in doc.findall("./Configurations/SVCConfiguration/Definition/" +
                            "ConfigurationProperties/PropertyArray/" +
                            "PropertySetProperty"):
        if prop.find("Key").text == 'isCached':
            prop.find("Value").text = "false"
        if prop.find("Key").text == 'maxRecordCount':
            prop.find("Value").text = maxRecords

    # Turn on feature access capabilities
    for prop in doc.findall("./Configurations/SVCConfiguration/Definition/Info/PropertyArray/PropertySetProperty"):
        if prop.find("Key").text == 'WebCapabilities':
            prop.find("Value").text = permissions_to_set

    # Add the namespaces which get stripped, back into the .SD
    root_elem.attrib["xmlns:typens"] = 'http://www.esri.com/schemas/ArcGIS/10.1'
    root_elem.attrib["xmlns:xs"] = 'http://www.w3.org/2001/XMLSchema'

    # Write the new draft to disk
    with open(newSDdraft, 'w') as f:
        doc.write(f, 'utf-8')

    # Analyze the service
    analysis = arcpy.mapping.AnalyzeForSD(newSDdraft)

    if analysis['errors'] == {}:
        # Stage the service
        arcpy.StageService_server(newSDdraft, outputSD)
        print("Created {}".format(outputSD))

    else:
        # If the sddraft analysis contained errors, display them and quit.
        print("Errors in analyze: \n {}".format(analysis['errors']))
        sys.exit()


if __name__ == "__main__":
    #
    # start

    print("Starting Feature Service publish process")

    # Turn all 'print' statements into a log-writing object
    Write_Print_To_Log(log_file)

    # Find and gather settings from the ini file
    localPath = sys.path[0]
    ##settingsFile = os.path.join(localPath, name_of_cfgFile) <MG 20180212: Commented out t oallow for full path to .ini>
    settingsFile = cfgFile  # <MG 20180212: Variable set at top of script>

    if os.path.isfile(settingsFile):
        print("Using INI file found at: {}.".format(settingsFile))
        config = ConfigParser.ConfigParser()
        config.read(settingsFile)
    else:
        print("INI file not found. \nMake sure a valid '.ini' file exists in the same directory as this script.")
        sys.exit()

    # AGOL Credentials
    inputUsername = config.get('AGOL', 'USER')
    inputPswd = config.get('AGOL', 'PASS')

    # FS values
    MXD = config.get('FS_INFO', 'MXD')
    serviceName = config.get('FS_INFO', 'SERVICENAME')
    folderName = config.get('FS_INFO', 'FOLDERNAME')
    tags = config.get('FS_INFO', 'TAGS')
    summary = config.get('FS_INFO', 'DESCRIPTION')
    maxRecords = config.get('FS_INFO', 'MAXRECORDS')

    # Share FS to: everyone, org, groups
    shared = config.get('FS_SHARE', 'SHARE')
    everyone = config.get('FS_SHARE', 'EVERYONE')
    orgs = config.get('FS_SHARE', 'ORG')
    groups = config.get('FS_SHARE', 'GROUPS')  # Groups are by ID. Multiple groups comma separated

    use_prxy = config.get('PROXY', 'USEPROXY')
    pxy_srvr = config.get('PROXY', 'SERVER')
    pxy_port = config.get('PROXY', 'PORT')
    pxy_user = config.get('PROXY', 'USER')
    pxy_pass = config.get('PROXY', 'PASS')

    proxyDict = {}
    if ast.literal_eval(use_prxy):
        http_proxy = "http://" + pxy_user + ":" + pxy_pass + "@" + pxy_srvr + ":" + pxy_port
        https_proxy = "http://" + pxy_user + ":" + pxy_pass + "@" + pxy_srvr + ":" + pxy_port
        ftp_proxy = "http://" + pxy_user + ":" + pxy_pass + "@" + pxy_srvr + ":" + pxy_port
        proxyDict = {"http": http_proxy, "https": https_proxy, "ftp": ftp_proxy}

    # create a temp directory under the script
    tempDir = os.path.join(localPath, "tempDir")
    if not os.path.isdir(tempDir):
        os.mkdir(tempDir)
    finalSD = os.path.join(tempDir, serviceName + ".sd")

    # initialize AGOLHandler class
    agol = AGOLHandler(inputUsername, inputPswd, serviceName, folderName, proxyDict)

    # Turn map document into .SD file for uploading
    print 'Using MXD at: {} to create .SD file'.format(MXD)
    makeSD(MXD, serviceName, tempDir, finalSD, maxRecords, tags, summary)

    # overwrite the existing .SD on arcgis.com
    if agol.upload(finalSD, tags, summary):

        # publish the sd which was just uploaded
        fsID = agol.publish()

        # share the item
        if ast.literal_eval(shared):
            agol.enableSharing(fsID, everyone, orgs, groups)

        print '\nDeleting tempDir...'
        shutil.rmtree(tempDir)
        print("\nFinished.")

    # End of script reporting
    print 'End of script'
    sys.stdout = orig_stdout
    print 'End of script'

##    raw_input('Press "ENTER" to continue...')
