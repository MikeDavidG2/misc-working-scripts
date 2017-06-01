""" IMPORTANT!!!
This script is a GitHub backup of a version the live version that is located
at:  P:\habitrak\Scripts\Python_Scripts\TestHabitrakParcels.py
This is because an ArcGIS tool has been created in the P:\habitrak\Scripts folder
that uses the live version.
"""
#-------------------------------------------------------------------------------
# Name:        SortHabitrakParcels.py
"""
  Purpose:   This script is to be used as a method of quickly sorting through
a list of parcels and testing those parcels
to see if that parcel needs to be 'analyzed by a human' or if it can be ignored
as not impacting MSCP because:
1.  It is either outside of the MSCP South boundary,
2.  It is in 100% urban vegetation,
3.  Or it has already been recorded as a loss.

Inputs are:
1.  A CSV file with APN numbers that should be tested
        (set with the  parcel_CSV_file_path variable)
2.  A few variables below that may need to change from year to year, or if
    different file structures are used than the one that I've used in 2016.

The outputs of this script are:
1.  A CSV file with APN of the parcel and the results of the series of tests for
    that parcel.
        (location for output is set with the loc_to_create_CSV_file variable)
2.  A featuree class: ParcelsToAnalyze_<year>_<month>_<day>__<hour>_<min>_<sec>.
    This FC will contain all of the parcels that need to be analyzed by a human
    appended to it.  The FC will be created inside inside the FGDB set by the
    loc_to_create_ParcelToAnalyze_FC variable.

Each function has a description of what steps it performs at the beginning of
  that functions definition.
The functions that are called (in order that the script calls them) are:
1.  main()
2.  GetParcelList()
3.  ProcessParcelList()
4.  CreateCSV
5.  CreateParcelToAnalyzeFC()

For each Parcel:
    6.  PerformAllTestParcels()
        a.  TestParcelLength()
        b.  TestParcelFound()
        c.  TestParcelInBoundary()
        d.  TestParcelInVeg()
        e.  TestParcelAlreadyRecorded()

    IF result of the PerformAllTestParcels() is NOT: 'HUMAN ANALYSIS NEEDED'
    7.  WriteToCSV()

    IF result  the PerformAllTestParcels() IS: 'HUMAN ANALYSIS NEEDED'
    7.  AppendParcelToFC()
    8.  WriteToCSV()

NOTE:  If the MXD has selections on it when it is saved and closed, the script
may produce bad results (i.e. if a selection is on one MSCP South polygon,
any parcel outside of the selected polygon--but still inside the MSCP South
Boundary--will be falsly given a 'Not in MSCP South Boundary' test result.
The solution is to make sure there are no selections in the
'MXD_To_Test_Parcels.mxd'
"""

# Author:      Mike Grue
#
# Created:     11/10/2016
# Copyright:   (c) mgrue 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, csv, time
from datetime import datetime

arcpy.env.overwriteOutput = True
#TODO: Add error handling to this whole script so someone else can debut it if
#  I'm not around

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              VARIABLES
#-------------------------------------------------------------------------------

#TODO: Can probably get rid of the 'year' variable and info about it below at
# some point...
#The'year' variable here used to be used before converting the script into an ArcGIS tool.
# It is no longer needed, but I have retained it below in case it is needed.
###What year is it?  This will be used to put the CSV files and the parcel polygons
###  into the correct folder in P:\habitrak\<year> folder.
##year = '2016'
##year = arcpy.GetParameterAsText(0)
#-------------------------------------------------------------------------------
#                Variables that are parameters in the script
#-------------------------------------------------------------------------------

#Location and name of CSV file with the parcels you want to test
##parcel_CSV_file_path = r"P:\habitrak\%s\List_Of_Parcels_CSVs\SeventhBatch.csv" % year
parcel_CSV_file_path = arcpy.GetParameterAsText(0)

#In what folder do you want to create the CSV file with the results of the test?
##loc_to_create_CSV_file = r'P:\habitrak\%s\BuildingPermits\Test_Results_CSVs' % year
loc_to_create_CSV_file = arcpy.GetParameterAsText(1)

#In What FGDB (9.3 FGDB) do you want to create the ParcelToAnalyze Feature Class?
##loc_to_create_ParcelToAnalyze_FC = r'P:\habitrak\%s\ParcelsToAnalyze.gdb' % year
loc_to_create_ParcelToAnalyze_FC = arcpy.GetParameterAsText(2)

#This should be pointing to the SDE source for ATLANTIC.sde
#Use the below as a template:
#r'Database Connections\<<your_connection_to_ATLANTIC_SDE_here>>'
##SDE_source_for_ATLANTIC = r'Database Connections\ad@ATLANTIC@SDE.sde'
SDE_source_for_ATLANTIC = arcpy.GetParameterAsText(3)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#             Variables that are constants and need to be changed
#                   below if they need editing
#-------------------------------------------------------------------------------

#The MXD with the layers described in the varables below
mxd = arcpy.mapping.MapDocument(r"P:\habitrak\Maps\MXD_To_Test_Parcels.mxd")

mxd_layer_name_for_parcels = 'SDE.SANGIS.PARCELS_ALL'

mxd_layer_name_for_MSCP_boundary = 'MSCP South Boundary'

mxd_layer_name_for_veg_with_no_urban = 'Regional Vegetation Except Urban (MSCP)'

#-------------------------------------------------------------------------------

#Where is the most current source for the Habitrak Footprints?
source_for_habitrak_footprints = r'P:\habitrak\data\County of San Diego.mdb\Projects\Projects'

#Where is the Loss table located?
habitrak_loss_table = r'P:\habitrak\data\County of San Diego.mdb\Loss'

#Where do you want the dissolved habitrak Loss footprints to go?
habitrak_loss_footprints_FGDB = r'P:\habitrak\data\HabiTrakLossProjectFootprints.gdb'

#Name of the loss footprints in the habitrak_loss_footprints_FGDB
habitrak_loss_footprints_name = 'Habitrak_Loss_Footprints'

#Name of the dissolved loss footprints in the habitrak_loss_footprints_FGDB
habitrak_loss_footprints_Diss_name = 'Habitrak_Loss_Footprints_Diss'


#-------------------------------------------------------------------------------
#                               Testing purposes
#-------------------------------------------------------------------------------


# For testing purposes use below CSV file for testing purposes, you should get
# the results listed below (in order).  You should only have to uncomment
# the below variable:
##parcel_CSV_file_path = r"P:\habitrak\2016\Building_Permits\List_Of_Parcels_CSVs\Parcel_Test.csv"
"""The results you should get are:
1st APN = WARNING Length of Parcel not correct
2nd     = WARNING Parcel not found
3rd     = Parcel not in MSCP South
4th     = Parcel 100% Urban
5th     = Parcel already recorded.  PROJECT NUMBER NEEDED.
6th     = HUMAN ANALYSIS NEEDED

user_entered_parcel_list = [1234567, 12345678, 52216105, 51926011, 51713122, 51510125]
"""


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#*************************    Start FUNCTIONS    *******************************
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#                              GetParcelList
#-------------------------------------------------------------------------------
"""This function gets a list of parcels to test from the parcel_CSV_file_path
variable and puts it into the user_entered_parcel_list variable in main()
"""
def GetParcelList(parcel_CSV_file_path_def):
    print 'Getting list of parcels from: ' + parcel_CSV_file_path_def
    user_entered_parcel_list_def = []

    with open(parcel_CSV_file_path_def, 'rb') as csvfile:
        my_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in my_reader:
            user_entered_parcel_list_def.append(', '.join(row))

    return user_entered_parcel_list_def


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              ProcessParcelList
#-------------------------------------------------------------------------------
"""This function adds the quotes to the user_entered_parcel_list so that it can
be in the correct format: 12345678 to '12345678'  and sends it to the
actual_parcel_list variable in main()
"""

def ProcessParcelList(user_entered_parcel_list_def):
    print 'Processing Parcel List'
    arcpy.AddMessage('Processing Parcel List')
    actual_parcel_list_def = []

    for parcel in user_entered_parcel_list_def:
        parcel = "'" + str(parcel) + "'"
        actual_parcel_list_def.append(parcel)

    return actual_parcel_list_def


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                           DissHabitrakLossFootprints
#-------------------------------------------------------------------------------
"""This function:
1. Copies the Habitrak Projects layer from a .mdb database to aFGDB so that we
   can perform geoprocessing tools on it.  It only copies the features that are
   considered losses: "[TYPE] = 2"
2. Dissolves the loss footprints"""

def DissHabitrakLossFootprints():

    in_features = source_for_habitrak_footprints
    out_path = habitrak_loss_footprints_FGDB
    out_name = habitrak_loss_footprints_name
    where_clause = "[TYPE] = 2"

    #Process
    arcpy.FeatureClassToFeatureClass_conversion(in_features, out_path, out_name, where_clause)

    #Dissolve the new feature class

    in_features = out_path + '\\' + out_name
    out_feature_class = out_path + '\\' + habitrak_loss_footprints_Diss_name
    dissolve_field = "#"
    statistics_fields = '#'
    multi_part = 'MULTI_PART'
    unsplit_lines = 'DISSOLVE_LINES'

    print 'Dissolving Habitrak Footprints to: %s' % out_feature_class
    arcpy.AddMessage('Dissolving Habitrak Footprints to: %s' % out_feature_class)
    #Process
    arcpy.Dissolve_management(in_features, out_feature_class, dissolve_field,
                                statistics_fields, multi_part, unsplit_lines)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              TestParcelLength
#-------------------------------------------------------------------------------
"""This function tests the parcel length to make sure it has 8 numbers in it
It returns if the series of tests should continue (if it has 8 numbers)
or not (if it does not have 8 characters)"""

def TestParcelLength(parcel_def):
    print '    Testing Parcel Length'
    arcpy.AddMessage('    Testing Parcel Length')
    cont = True

    #Test to make sure there are 8 numbers in the APN (8 + the two ' = 10)
    if (len(parcel_def) == 10):
        pass
        print '        Length OK!'
        arcpy.AddMessage('        Length OK!')
    else:
        #Do not continue if the parcel is not the correct length
        print '        Incorrect Length!'
        arcpy.AddMessage('        Incorrect Length!')
        cont = False

    return cont


#-------------------------------------------------------------------------------
#TODO: Can probably be deleted at some point
##def selectParcel(parcel_def):
##        # Try to select the parcel
##    in_layer_or_view = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_parcels)[0]
##    selection_type = 'NEW_SELECTION'
##    where_clause = "APN_8 =" + parcel_def
##
##    #Process
##    arcpy.SelectLayerByAttribute_management (in_layer_or_view, selection_type, where_clause)
##    return in_layer_or_view

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              TestParcelFound
#-------------------------------------------------------------------------------
"""This function tests to make sure that the parcel can be found from the
mxd_layer_name_for_parcels source.  It stops the series of tests if the parcel
cannot be found."""

def TestParcelFound(parcel_def):
    print '    Testing if Parcel is Found'
    arcpy.AddMessage('    Testing if Parcel is Found')
    cont = True

    # Try to select the parcel
    in_layer_or_view = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_parcels)[0]
    selection_type = 'NEW_SELECTION'
    where_clause = "APN_8 =" + parcel_def

    #Process
    arcpy.SelectLayerByAttribute_management (in_layer_or_view, selection_type, where_clause)

    #---------------------------------------------------------------------------
    # Was the parcel selected?
    countOfSelected = arcpy.GetCount_management(in_layer_or_view)
    count = int(countOfSelected.getOutput(0))

    if count == 1:
        print '        Parcel Found!'
        arcpy.AddMessage('        Parcel Found!')
        ##for row in arcpy.SearchCursor(in_layer_or_view):
            ##pass

    else:
        #Do not continue if there is no selection, the parcel was not found
        print '        Parcel NOT Found!'
        arcpy.AddMessage('        Parcel NOT Found!')
        cont = False

    return cont


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                            TestParcelInBoundary
#-------------------------------------------------------------------------------
"""This function tests if a parcel is at least partially inside the MSCP South
boundary, if so, the script continues, if the parcel is completely outside
the script returns that the series of tests should not continue because the parcel
is outside the MSCP South boundary"""

def TestParcelInBoundary(parcel_def):
    print '    Testing if Parcel is in Boundary'
    arcpy.AddMessage('    Testing if Parcel is in Boundary')
    cont = True

    # Keep the parcel selected if it intersects the mxd_layer_name_for_MSCP_boundary layer
    in_layer_or_view = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_parcels)[0]
    overlap_type = 'INTERSECT'
    select_features = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_MSCP_boundary)[0]
    search_distance = '#'
    selection_type = 'SUBSET_SELECTION'

    #Process
    arcpy.SelectLayerByLocation_management (in_layer_or_view, overlap_type,
                              select_features, search_distance, selection_type)

    #---------------------------------------------------------------------------
    # Is the parcel still selected?
    result = arcpy.GetCount_management(in_layer_or_view)
    count = int(result.getOutput(0))

    if count == 1:
        print '        Parcel in Boundary!'
        arcpy.AddMessage('        Parcel in Boundary!')
        for row in arcpy.SearchCursor(in_layer_or_view):
            ##print 'Parcel \'' + row.APN_8 + '\' INTERSECTS the MSCP South Boundary'
            pass

    else:
        # It does NOT appear that this parcel intersects the MSCP South Boundary
        #Do not continue if there is no selection
        print '        Parcel NOT in Boundary!'
        arcpy.AddMessage('        Parcel NOT in Boundary!')
        cont = False

    return cont


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              TestParcelInVeg
#-------------------------------------------------------------------------------
"""This function tests to see if a parcel intersects with the
mxd_layer_name_for_veg_with_no_urban layer.  This layer should not include
any Urban vegetation, so if there is no intersection at all, then the parcel
is NOT worth looking at and can be considered 100% Urban."""

def TestParcelInVeg(parcel_def):
    print '    Testing if parcel is in Veg'
    arcpy.AddMessage('    Testing if parcel is in Veg')
    cont = True

    #---------------------------------------------------------------------------
    #Keep the parcel selected if it intersects with the
    #mxd_layer_name_for_veg_with_no_urban layer
    in_layer_or_view = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_parcels)[0]
    overlap_type = 'INTERSECT'
    select_features = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_veg_with_no_urban)[0]
    search_distance = '#'
    selection_type = 'SUBSET_SELECTION'

    #Process
    arcpy.SelectLayerByLocation_management (in_layer_or_view, overlap_type, select_features, search_distance, selection_type)

    #---------------------------------------------------------------------------
    # Is the parcel still selected?
    result = arcpy.GetCount_management(in_layer_or_view)
    count = int(result.getOutput(0))

    if count == 1:
        print '        Parcel in Veg!'
        arcpy.AddMessage('        Parcel in Veg!')
        ##for row in arcpy.SearchCursor(in_layer_or_view):
            ##pass

    else:
        #Do not continue if there is no selection, parcel is not in veg
        print '        Parel NOT in Veg!'
        arcpy.AddMessage('        Parel NOT in Veg!')
        cont = False

    return cont


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                      TestParcelAlreadyRecorded
#-------------------------------------------------------------------------------
"""This function tests to see if the parcel is completely covered by existing
habitrak loss footprints.  These are the footprints created in the
DissHabitrakLossFootprints() function.  If the whole parcel is already
considered a loss, we do not need to look at the parcel further."""
#TODO: This function is not optimized because the 'WITHIN' setting for this
#  SelectLayerByLocation_management tool is returning parcels to be analyzed
#  when they really should be 'Previously recorded'.  It is OK though since this
#  tool errs on the side of caution and will make the user analyze the parcel.
#  This is only a 'to do' if I can figure out a way to make this function more
#  accurate.

def TestParcelAlreadyRecorded(parcel_def):
    print '    Testing if Parcel Already Recorded'
    arcpy.AddMessage('    Testing if Parcel Already Recorded')
    cont = True

    #Create a layer in memory of FC Habitrak_Losses_Diss
    #This has to be done since we are geoprocessing an SDE layer
    #And then want to perform a selection based on the result of that geoprocess
    in_features = habitrak_loss_footprints_FGDB + '\\' + habitrak_loss_footprints_Diss_name
    out_layer = 'habitrak_loss_footprints_Diss_lyr'

    #Process
    arcpy.MakeFeatureLayer_management (in_features, out_layer)

    #---------------------------------------------------------------------------

    #Keep the Parcel selected if it is within habitrak_footprints_diss
    in_layer_or_view = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_parcels)[0]
    overlap_type = 'WITHIN'
    select_features = 'habitrak_loss_footprints_Diss_lyr'
    search_distance = '#'
    selection_type = 'SUBSET_SELECTION'

    #Process
    arcpy.SelectLayerByLocation_management (in_layer_or_view, overlap_type, select_features, search_distance, selection_type)
    #---------------------------------------------------------------------------
    # Is the parcel still selected?
    result = arcpy.GetCount_management(in_layer_or_view)
    count = int(result.getOutput(0))

    if count == 1:
        #Do not continue if the parcel is still selected because it will remain
        #Selected if it falls completely within the habitrak footprint layer
        print '        Parcel already recorded!'
        arcpy.AddMessage('        Parcel already recorded!')
        cont = False

    else:
        print '        Parcel NOT yet recorded!'
        arcpy.AddMessage('        Parcel NOT yet recorded!')

    return cont

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                           Get_Prev_Capt_TR
#-------------------------------------------------------------------------------
"""This function is called whenever a parcel has been found to have been
previously recorded.  This function finds the previous tracking number and
returns that number so it doesn't have to be manually looked up.
"""
def Get_Prev_Tracking_Num(parcel_def):
    arcpy.AddMessage('Getting Previous Captured TR#...')
    #---------------------------------------------------------------------------
    # Create a layer view of the 'Projects' in a FGDB
    lossFootprints = habitrak_loss_footprints_FGDB + '\\' + habitrak_loss_footprints_name
    arcpy.MakeFeatureLayer_management(lossFootprints, 'lossFootprints')

    # Create a table fiew of the 'Loss' table
    arcpy.MakeTableView_management(habitrak_loss_table, 'lossTable')

    #---------------------------------------------------------------------------
    # Now Join the Loss table to the Projects Feature Layer
    in_layer_or_view = 'lossFootprints'
    in_field         = 'PROJECTID'
    join_table       = 'lossTable'
    join_field       = 'PROJECTID'
    join_type        = 'KEEP_ALL'
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    #---------------------------------------------------------------------------
    # make feature layer of parcels
    parcels_path = SDE_source_for_ATLANTIC + '\\SDE.SANGIS.PARCELS_ALL'
    arcpy.MakeFeatureLayer_management(parcels_path, 'parcels_layer')

    # Select the parcel
    in_layer_or_view = 'parcels_layer'
    selection_type = 'NEW_SELECTION'
    where_clause = "APN_8 =" + parcel_def

    arcpy.SelectLayerByAttribute_management (in_layer_or_view, selection_type, where_clause)

    #---------------------------------------------------------------------------
    # If not parcels selected, we don't want to continue
    result = arcpy.GetCount_management(in_layer_or_view)
    count = int(result.getOutput(0))

    if count == 0:
        tracking_num = 'Parcel not selected.  Tracking Number couldn\'t be determined.'
        return tracking_num
    #---------------------------------------------------------------------------

    # Select the project the parcel intersects
    arcpy.AddMessage('Selecting the project the parcel intersects')
    in_layer_or_view = 'lossFootprints'
    overlap_type = 'INTERSECT'
    select_features = 'parcels_layer'
    search_distance = ''
    selection_type = 'NEW_SELECTION'

    arcpy.SelectLayerByLocation_management(in_layer_or_view, overlap_type, select_features, search_distance, selection_type)

    #---------------------------------------------------------------------------
    # If no project is selected, we don't want to continue
    result = arcpy.GetCount_management(in_layer_or_view)
    count = int(result.getOutput(0))
    if count == 0:
        tracking_num = 'No project selected.  Tracking Number coultn\'t be determined.'
        return tracking_num
    #---------------------------------------------------------------------------

    # Get the TR # of the selected project
    field = 'Loss.TRACKNO'
    cursor = arcpy.SearchCursor('lossFootprints')
    row = cursor.next()
    projects = []

    while row:
        project = row.getValue(field)
        projects.append(project)
        row = cursor.next()

    # Make string of the project(s)
    # If there are more than one project, make a string readable and return it
    # to PerformAllTestParcels
    tracking_num = ' and '.join(projects)

    return tracking_num

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                         PerformAllTestParcels
#-------------------------------------------------------------------------------
"""This is the master testing function that runs through all of the tests and
prints outthe results of the tests, it returns the results back to the
main() function"""

def PerformAllTestParcels(parcel_def):
    #Get the year so it can be written to
    currentTime = datetime.now()
    year = str(currentTime.year)

        # Test the length of the parcel (should be 8 numbers)
    lengthGood = TestParcelLength(parcel_def)

    # If length is good, continue to the next test...
    if lengthGood == True:
        parcelFound = TestParcelFound(parcel_def)

        # If parcel is found, continue to the next test...
        if parcelFound == True:
            inBoundary = TestParcelInBoundary(parcel_def)

            # If parcel is in the MSCP South boundary, continue...
            if inBoundary == True:
                inVeg = TestParcelInVeg(parcel_def)

                #If parcel is in vegetation, continue...
                if inVeg == True:
                    notYetRecorded = TestParcelAlreadyRecorded(parcel_def)

                    # If the parcel has not yet been recorded, then it needs to
                    # be looked at
                    if notYetRecorded == True:
                        testResult = 'HUMAN ANALYSIS NEEDED'

                    # The parcel received a 'False' for the notYetRecorded variable
                    # The parcel has already been recorded
                    else:
                        tracking_num = Get_Prev_Tracking_Num(parcel_def)
                        testResult = 'Write on BP:  "%s Previously Rec Loss, TR #: %s' % (year, tracking_num)

                # The parcel received a 'False' for the inVeg variable
                # The parcel only exists in 'Urban' vegetation
                else:
                    testResult = 'Write on BP: "' + year + ' 100% Urban"'

            # The parcel received a 'False' for the inBoundary variable
            # The parcel is not in MSCP South
            else:
                testResult = 'Write on BP: "%s Not in MSCP South"' % year

        # The parcel received a 'False' for the parcelFound variable
        # The parcel isn't in the parcels layer
        else:
            testResult = 'WARNING Parcel not found, double check the APN'

    # The parcel received a 'False' for the lengthGood variable
    # The parcel does not have 8 numbers in it
    else:
        testResult = 'WARNING Length of Parcel not correct, double check the APN'

    return testResult


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              CreateCSV
#-------------------------------------------------------------------------------
"""This function creates a CSV file with headers to act as the 'report' for all
of the tests.  It will be created at the path set for the loc_to_create_CSV_file
variable and returns the full path to the newly created CSV.  The name of the
file is determined by todays date and time.
"""

def CreateCSV(loc_to_create_CSV_file_def):
    print 'Creating CSV file at: %s' % loc_to_create_CSV_file_def
    arcpy.AddMessage('Creating CSV file at: %s' % loc_to_create_CSV_file_def)

    #Create a unique name for the CSV file based on the date and time
    currentTime = datetime.now()
    date = '%s_%s_%s' % (currentTime.year, currentTime.month, currentTime.day)
    time = '%s_%s_%s' % (currentTime.hour, currentTime.minute, currentTime.second)
    CSV_file = loc_to_create_CSV_file_def + '\\HabitrakTestResults_' + date + '__' + time + '.csv'

    #Set the headers for the file
    headers = ['APN', 'Test Result']

    #Create the CSV
    with open(CSV_file, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)

    #Return the path to the CSV_file so that it can be used to append data to
    # in the WriteToCSV function
    return CSV_file


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              WriteToCSV
#-------------------------------------------------------------------------------
"""This function is called whenever a parcel has completed its series of tests
It writes the APN and result of the tests to the CSV file in the CSV_file_path
variable
"""

def WriteToCSV(CSV_file_path_def, parcel_def, result_from_parcel_test_def):
    print 'Writing %s to CSV' % parcel_def
    arcpy.AddMessage('Writing %s to CSV' % parcel_def)

    #Set the info for the parcel
    parcel_info = [parcel_def, result_from_parcel_test_def]

    #Set the location for the CSV file
    CSV_file = CSV_file_path_def

    with open(CSV_file, 'ab') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(parcel_info)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              CreateParcelToAnalyzeFC
#-------------------------------------------------------------------------------
"""This function creates a Feature class (to act as a container for all of the
parcels that need to have a human analyze it) in the 9.3 FGDB located at the
loc_to_create_ParcelToAnalyze_FC variable.  It names the FC based on todays
date and time so it returns the path and name of the FC so that it can be
accessed when we want to write a parcel to the new FC.  It will also create
an APN field so we know what parcel number each shape belongs to.
"""

def CreateParcelToAnalyzeFC(loc_to_create_ParcelToAnalyze_FC_def):
    #Create Feature Class
    print 'Creating ParcelToAnalyze FC at: %s' % loc_to_create_ParcelToAnalyze_FC_def
    arcpy.AddMessage('Creating ParcelToAnalyze FC at: %s' % loc_to_create_ParcelToAnalyze_FC_def)

    #Create a unique name for the FC based on the date and time
    currentTime = datetime.now()
    date = '%s_%s_%s' % (currentTime.year, currentTime.month, currentTime.day)
    time = '%s_%s_%s' % (currentTime.hour, currentTime.minute, currentTime.second)
    FC_name = 'ParcelsToAnalyze_' + date + '__' + time

    #Set variables
    out_path = loc_to_create_ParcelToAnalyze_FC_def
    out_name = FC_name
    geometry_type = "POLYGON"
    template = '#'
    has_m = 'DISABLED'
    has_z= 'DISABLED'
    spatial_reference = source_for_habitrak_footprints

    #Process
    arcpy.CreateFeatureclass_management (out_path, out_name, geometry_type,
                                      template, has_m, has_z, spatial_reference)

    #---------------------------------------------------------------------------
    #Create APN field

    in_table = out_path + '\\' + out_name
    field_name = 'APN_8'
    field_type = 'TEXT'
    field_precision = '#'
    field_scale = '#'
    field_length = '8'
    field_alias = '#'
    field_is_nullable = 'NULLABLE'
    field_is_required = 'NON_REQUIRED'
    field_domain = '#'

    #Process
    arcpy.AddField_management (in_table, field_name, field_type,
                                field_precision, field_scale, field_length,
                                field_alias, field_is_nullable,
                                field_is_required, field_domain)

    FC_path_def = loc_to_create_ParcelToAnalyze_FC_def + '\\' + FC_name

    return FC_path_def


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              AppendParcelToFC
#-------------------------------------------------------------------------------
"""This function is called when a parcel has been tested and results in
'HUMAN ANALYSIS NEEDED'.  This function will append the parcels to the FC
created in the CreateParcelToAnalyzeFC() function.
"""

def AppendParcelToFC(FC_path_def, parcel_def):
    print 'Appending Parcel %s to FC' % parcel_def
    arcpy.AddMessage('Appending Parcel %s to FC' % parcel_def)

    #Select the parcel
    in_layer_or_view = arcpy.mapping.ListLayers(mxd, mxd_layer_name_for_parcels)[0]
    selection_type = 'NEW_SELECTION'
    where_clause = "APN_8 =" + parcel_def

    #Process
    arcpy.SelectLayerByAttribute_management (in_layer_or_view, selection_type, where_clause)

    #---------------------------------------------------------------------------
    #Make sure we have one parcel selected before we do an append
    countOfSelected = arcpy.GetCount_management(in_layer_or_view)
    count = int(countOfSelected.getOutput(0))

    ##print 'Count is: ' + str(count)


    if count == 1:
        inputs = in_layer_or_view
        target = FC_path_def
        schema_type = 'NO_TEST'
        field_mapping = '#'
        subtype = '#'

        #Process
        arcpy.Append_management(inputs, target, schema_type, field_mapping, subtype)

    else:
        print '    WARNING.  Count of selected parcels to append was not 1!  Append not attempted'
        arcpy.AddMessage('    WARNING.  Count of selected parcels to append was not 1!  Append not attempted')


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#*************************    Start MAIN    ************************************
#-------------------------------------------------------------------------------
"""Main function"""

def main():
    startTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print 'Starting MAIN at: %s\n' % startTime
    arcpy.AddMessage('Starting MAIN at: %s\n' % startTime)

    #Get a list of user defined parcels
    user_entered_parcel_list = GetParcelList(parcel_CSV_file_path)


    #Send the user_entered_parcel_list to get the ' added to the beginning and
    # endof the APN
    actual_parcel_list = ProcessParcelList(user_entered_parcel_list)

    #Dissolve the 'Loss' footprints and put them into a FGDB
    DissHabitrakLossFootprints()

    #Create a CSV file at the loc_to_create_CSV_file
    CSV_file_path = CreateCSV(loc_to_create_CSV_file)

    #Create a Feature Class to hold the geometry of all of the
    # HUMAN ANALYSIS NEEDED parcels
    FC_path = CreateParcelToAnalyzeFC(loc_to_create_ParcelToAnalyze_FC)

    #Counter for the number of processed parcels
    num_parcels_processed = 1

    for parcel in actual_parcel_list:
        print '\nTesting parcel: %s (%s of %s)' % (parcel, str(num_parcels_processed), str(len(user_entered_parcel_list)))
        arcpy.AddMessage('\nTesting parcel: %s (%s of %s)' % (parcel, str(num_parcels_processed), str(len(user_entered_parcel_list))))

        #Send the parcel into 'PerformAllTestParcels' function which will send
        #the Parcel to all of the sub functions that will run the individual tests
        result = PerformAllTestParcels(parcel)
        print result
        arcpy.AddMessage(result)

        #If the result from the PerformAllTestParcels is anything other than
        # HUMAN ANALYSIS NEEDED, then we can simply write this parcel's APN and
        # result to a CSV file.
        if (result != 'HUMAN ANALYSIS NEEDED'):
            WriteToCSV(CSV_file_path, parcel, result)

        #Else, the result from PerformAllTestParcels was HUMAN ANALYSIS NEEDED
        # and therefore, we need to export this parcel to the
        # ParcelsToAnalyze_<date>
        else:
            AppendParcelToFC(FC_path, parcel)
            WriteToCSV(CSV_file_path, parcel, result)

        num_parcels_processed += 1

    finishTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print '\n\nFinished MAIN at: %s' % finishTime
    arcpy.AddMessage('\n\nFinished MAIN at: %s' % finishTime)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                              Call Main Function
#-------------------------------------------------------------------------------
"""This line actually calls main()"""

if __name__ == '__main__':
    main()

