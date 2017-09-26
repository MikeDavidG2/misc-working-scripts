#-------------------------------------------------------------------------------
# Name:        Unregister_Replicas_on_AGOL_FS.py
# Purpose:
"""

"""
#
# Author:      mgrue
#
# Created:     14/09/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():

    #---------------------------------------------------------------------------
    #                          Set Variables
    cfgFile = r"C:\Users\mgrue\Documents\accounts.txt"

    name_of_FS = raw_input('What is the name of the Feature Service you want to unregister? ')

    #---------------------------------------------------------------------------
    #                          Start Calling Functions

    token = Get_Token(cfgFile)

    Unregister_AGOL_Replica_Ids(name_of_FS, token)


#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------
#                              Define Functions
#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------

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
    usr = configRMA.get("mgrue","usr")
    pwd = configRMA.get("mgrue","pwd")

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
#                 FUNCTION:  Unregister AGOL Replica IDs

def Unregister_AGOL_Replica_Ids(name_of_FS, token):
    """
    PARAMETERS:
      name_of_FS (str): The name of the Feature Service (do not include things
        like "services1.arcgis.com/1vIhDJwtG5eNmiqX/ArcGIS/rest/services", just
        the name is needed.  i.e. "DPW_WP_SITES_DEV_VIEW".
      token (str): Obtained from the Get_Token().

    RETURNS:
      None

    FUNCTION:
      To be used to get a list of replicas for an AGOL Feature Service and then
      ask the user if they wish to unregister the replicas that were listed.
      This will primarily be used to be allowed to overwrite an existing FS that
      has replicas from other users who have not removed a map from Collector.

    NOTE: This function assumes that you have obtained a Token with Get_Token()
    """
    print '--------------------------------------------------------------------'
    print 'Starting Unregister_AGOL_Replica_Ids()'
    import urllib2, urllib, json
    success = True
    #---------------------------------------------------------------------------
    #              Get list of Replicas for the Feature Service

    # Set the URLs
    list_replica_url     = r'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/{}/FeatureServer/replicas'.format(name_of_FS)
    query                = '?f=json&token={}'.format(token)
    get_replica_list_url = list_replica_url + query
    ##print get_replica_list_url

    # Get the replicas
    try:
        print '  Getting replicas for: {}'.format(name_of_FS)
        response = urllib2.urlopen(get_replica_list_url)
        replica_json_obj = json.load(response)
        ##print replica_json_obj

        if len(replica_json_obj) == 0:
            print '  No replicas for this feature service.'
        else:
            #-----------------------------------------------------------------------
            #               Print out the replica ID and username owner
            for replica in replica_json_obj:
                print '  Replica: {}'.format(replica['replicaID'])

                list_replica_url = r'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/{}/FeatureServer/replicas/{}'.format(name_of_FS, replica['replicaID'])
                query            = '?f=json&token={}'.format(token)
                replica_url      = list_replica_url + query
                response = urllib2.urlopen(replica_url)
                owner_json_obj = json.load(response)
                print '  Is owned by: {}\n'.format(owner_json_obj['replicaOwner'])

                # Ask user if they want to unregister the replicas mentioned above
                unregister_replicas = raw_input('Do you want to unregister the above replicas? (y/n)')
    except Exception as e:
        success = False
        print '*** ERROR with Getting the Replicas ***'
        print str(e)
        if str(e) == 'string indices must be integers':
            print '  May be a problem with the token\'s permissions to perform the requested action.'

    if success:
        try:
            #-----------------------------------------------------------------------
            #                      Unregister Replicas
            if unregister_replicas == 'y':
                for replica in replica_json_obj:
                    print '  Unregistering replica: {}'.format(replica['replicaID'])
                    unregister_url = r'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/ArcGIS/rest/services/{}/FeatureServer/unRegisterReplica?token={}'.format(name_of_FS, token)
                    unregister_params = urllib.urlencode({'replicaID': replica['replicaID'], 'f':'json'})

                    response = urllib2.urlopen(unregister_url, unregister_params)
                    unregister_json_obj = json.load(response)
                    print '    Success: {}'.format(unregister_json_obj['success'])
        except Exception as e:
            print '*** ERROR with Unregistering Replicas ***'
            print str(e)

    if success:
        print 'Successfully finished Unregister_AGOL_Replica_Ids()'
    else:
        print 'Error with Unregister_AGOL_Replica_Ids()'
#-------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
