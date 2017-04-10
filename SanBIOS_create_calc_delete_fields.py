#-------------------------------------------------------------------------------
# Name:        module1

"""Purpose of this script is two fold depending if the user wants to add and calculate fields or delete fields after appending to SDW:

    To create the fields that are needed in SDE
    Join the tables that act as domains
    Calculate the new fields
    Give user a list of tasks to perform manually

    OR

    Delete the new fields now that they are no longer needed
"""
#
# Author:      mgrue
#
# Created:     07/04/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# TODO: document this script
# TODO: get the polygons working on this script too
# TODO: put this script in the SanBIOS folder

import arcpy, os
arcpy.env.overwriteOutput = True

def main():

    #                            Set variables

    # Location of data
    sanbios_fgdb     = r'P:\SanBIOS\Geodatabase\SANBIOS.gdb'
    sanbios_pts_cn   = sanbios_fgdb + '\\' + r'observations\SANBIOS_PTS_CN'
    sanbios_poly_cn  = sanbios_fgdb + '\\' + r'observations\SANBIOS_POLY_CN'
    fc_list = [sanbios_pts_cn, sanbios_poly_cn]
    fc_list = [sanbios_poly_cn, sanbios_pts_cn]

    # Name of fields to be added
    field_list   = ['MASTER_LAT', 'MASTER_COM', 'STATUS', 'DEPTNAME', 'LIFEFORM', 'ORIGINDESC', 'PNAME', 'SITEQUALDE', 'SOURCE_NAM']

    # Get use input on which functions should be called
    add_or_delete = raw_input ('Do you want to add fields and calculate fields? OR delete fields added by this script? \nType: ("add"/"delete")')

    #---------------------------------------------------------------------------
    #                        Add and calculate fields

    # Add and calculate fields if user wants
    if (add_or_delete == 'add'):

        # Do the process for both points and polys
        for fc in fc_list:

            print 'Performing process for: {}\n\n'.format(fc)
            # Create fields
            Add_Fields(fc, field_list)

            # Perform join and calc fields
            Join_Calc_Fields(fc, sanbios_fgdb)

            print '\n-----------------------------------------------------------\nDone with process for: {}\n\n'.format(fc)

        # Give the user a list of steps they still need to perform
        User_Steps_ToDo(sanbios_fgdb)

    #---------------------------------------------------------------------------
    #                            Delete fields

    # Delete fields if user wants
    elif (add_or_delete == 'delete'):

        print 'NOTE: This process is typically run after appending data to SDW. \nFields which will be deleted are:'
        for field in field_list:
            print '  ' + field

        delete_ok = raw_input ('...OK to delete fields? (y/n)')

        if delete_ok == 'y':
            for fc in fc_list:

                print 'Deleting fields for: {}'.format(fc)

                arcpy.DeleteField_management(fc, field_list)

        else:
            print 'Fields not deleted.'

    # Triggered if user does not enter 'add' or 'delete'.
    else:
        print 'Please enter "add" or "delete".'

    print 'Successfully completed script.'
    raw_input ('Press ENTER to finish script.')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                          Start defining FUNCTIONS
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#                            FUNCTION Add_fields()

def Add_Fields(input_table, field_list):

    """ This function adds the needed fields to the FGDB SANBIOS_PTS_CN"""
    print 'Starting Add_Fields()'


    for field in field_list:
        in_table          = input_table
        field_name        = field
        field_type        = 'TEXT'
        field_precision   = ''
        field_scale       = ''
        field_length      = 255
        field_alias       = ''
        field_is_nullable = ''
        field_is_required = ''
        field_domain      = ''

        try:
            print '  Adding field: ' + field
            arcpy.AddField_management(in_table, field_name, field_type, field_precision,
                                  field_scale, field_length, field_alias,
                                  field_is_nullable, field_is_required, field_domain)
        except:
            print '  Couln\'t add field: ' + field

    print 'Finished Add_Fields()\n'

#-------------------------------------------------------------------------------
#                       FUNCTION: Join_Calc_Fields()

def Join_Calc_Fields(master_table, sanbios_fgdb):

    """This function:
        1. Defines the tables that need to be joined to the master_table
        2. Makes views for those tables
        3. Makes a layer for the master_table (FGDB: SANBIOS_PTS_CN)
        4. Joins all the tables to the master_table
        5. Performs the calculations for those fields
    """

    print 'Starting Join_Calc_Fields()'

    # Define tables to join to master_table
    departments_tbl  = sanbios_fgdb + '\\' + r'Departments'
    life_form_tbl    = sanbios_fgdb + '\\' + r'LifeForm'
    origin_tbl       = sanbios_fgdb + '\\' + r'Origin'
    precision_tbl    = sanbios_fgdb + '\\' + r'Precision'
    site_quality_tbl = sanbios_fgdb + '\\' + r'SiteQuality'
    source_tbl       = sanbios_fgdb + '\\' + r'Source'
    species_tbl      = sanbios_fgdb + '\\' + r'Species'

    tables_list = [departments_tbl, life_form_tbl, origin_tbl, precision_tbl,
                   site_quality_tbl, source_tbl, species_tbl]

    #---------------------------------------------------------------------------
    # Make views for all tables
    for table in tables_list:
        view_name = os.path.basename(table) + '_view'
        print '  Making table view from table: ' + table
        print '    Named: ' + view_name

        arcpy.MakeTableView_management(table, view_name)

    # Make layer for master_table
    print '  Making feature layer from FC: ' + master_table
    master_table_lyr = 'master_table_lyr'
    print '    Named: {}\n'.format(master_table_lyr)

    arcpy.MakeFeatureLayer_management(master_table, master_table_lyr)

    #---------------------------------------------------------------------------
    #                           Join tables to master_table
    # Constants for table joins
    in_layer_or_view = master_table_lyr
    join_type = 'KEEP_ALL'


    # Perform joins
    in_field   = 'DeptID'
    join_table = 'Departments_view'
    join_field = 'DeptID'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    in_field   = 'LifeID'
    join_table = 'LifeForm_view'
    join_field = 'LifeID'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    in_field   = 'OriginID'
    join_table = 'Origin_view'
    join_field = 'OriginID'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    in_field   = 'PCode'
    join_table = 'Precision_view'
    join_field = 'PCode'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    in_field   = 'SiteQualID'
    join_table = 'SiteQuality_view'
    join_field = 'SiteQualID'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    in_field   = 'SourceID'
    join_table = 'Source_view'
    join_field = 'SourceID'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    in_field   = 'spID'
    join_table = 'Species_view'
    join_field = 'spID'
    print '  Joining: {} with: {} based on in_field: {} and join_field: {}\n'.format(in_layer_or_view, join_table, in_field, join_field)
    arcpy.AddJoin_management(in_layer_or_view, in_field, join_table, join_field, join_type)

    #---------------------------------------------------------------------------
    #                      Perform field calculations

    # Print the field names (used during testing)
##    for field in arcpy.ListFields(master_table_lyr):
##        print field.name

    # Constants for calculations
    in_table        = master_table_lyr
    expression_type = 'PYTHON_9.3'
    code_block      = ''
    fc_name         = os.path.basename(master_table)

    # Calculate fields
    field      = "{}.DEPTNAME".format(fc_name)
    expression = '!Departments.DeptName!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.LIFEFORM".format(fc_name)
    expression = '!LifeForm.LifeForm!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.ORIGINDESC".format(fc_name)
    expression = '!Origin.OriginDesc!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.PNAME".format(fc_name)
    expression = '!Precision.PName!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.SITEQUALDE".format(fc_name)
    expression = '!SiteQuality.SiteQualDe!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.SOURCE_NAM".format(fc_name)
    expression = '!Source.source_nam!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.MASTER_LAT".format(fc_name)
    expression = '!Species.master_lat!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.MASTER_COM".format(fc_name)
    expression = '!Species.master_com!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    field      = "{}.STATUS".format(fc_name)
    expression = '!Species.Status!'
    print '  Calculating field: "{}" in table: "{}" equal to: "{}"'.format(field, in_table, expression)
    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block)

    print '\nFinished Join_Calc_Fields()\n'

#-------------------------------------------------------------------------------

#                              FUNCTION: User_Steps_ToDo()

def User_Steps_ToDo(sanbios_fgdb):
    """ This function gives the user a list of steps they still need to do on their own
    """

    print 'Starting User_Steps_ToDo()'

    print """  This script has:
    1. Created the fields needed in order to go into the SDE.SANBIOS_POINTS_CN and SDE.SANBIOS_POLY_CN
    2. Joined the FGDB SANBIOS_POINTS_CN and SANBIOS_POLY_CN Feature Classes to the various tables acting as domains
    3. Calculated the new fields based on those joins

  What the USER STILL NEEDS TO DO before this process is finished:
    1. View the Feature Classes in:\n    {}\n    and ensure that all the fields exist that should and that the data has been copied from the join tables
    2. In the SDW (Workspace) FC, use the Delete Features Tool to remove the existing data in SDW FC
    3. Append the data from the FGDB SANBIOS_POINTS_CN or SANBIOS_POLY_CN to the corresponding SDW FC
    4. Change the dates in SDW.PDS.LUEG_UPDATES for [LAYER_NAME] SANBIOS_POLY_CN and SANBIOS_PTS_CN
    5. Delete the fields that were added during this script.  Can be done manually, or by running this script again and choosing to run the Delete_Added_Fields function.
    """.format(sanbios_fgdb)

    print 'Finished User_Steps_ToDo()'

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
