#-------------------------------------------------------------------------------
# Name:        Search_FeatureClasses.py
# Purpose:
"""
Set the 'workspace', 'prefix' and 'wild_card' variables to search for layers
in the workspace database.

Can be used to generate CSV lists of all the objects in an SDE
"""
#
# Author:      mgrue
#
# Created:     18/01/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os

def main():
    #---------------------------------------------------------------------------
    #                              Set variables

    # Change workspace to database you want to list FC's
    workspace = 'Database Connections\AD@ATLANTIC@SDW.sde'
    ##workspace = 'Database Connections\AD@ATLANTIC@SDE.sde'

    # Change to the prefix that is at the beginning of each FC to list
    prefix    = 'SDW.PDS.'
    ##prefix    = 'SDE.SANGIS.'

    # Set wildcard to limit searches in the name of the FC
    wild_card = '*'

    #---------------------------------------------------------------------------
    #           List FC's in a form that can be imported into a CSV
    arcpy.env.workspace = workspace

    # Get lists
    print 'Getting List of Datasets'
    datasets = arcpy.ListDatasets(prefix + wild_card)

    print 'Getting list of Feature Classes'
    fcs      = arcpy.ListFeatureClasses(prefix + wild_card)

    print 'Getting lists of Tables'
    tables   = arcpy.ListTables(prefix + wild_card)


    # Sort lists
    datasets.sort()
    fcs.sort()


    # Print list of FC's that are in a Dataset
    print 'Datasets: '
    for dataset in datasets:
        ##print dataset
        for fc in arcpy.ListFeatureClasses(feature_dataset = dataset):
            path = os.path.join(workspace, dataset, fc)
            print '%s, %s' % (dataset, path)

    # Print list of FC's that are NOT in a Dataset
    print '\n\nFeature Classes: '
    for fc in fcs:
        path = os.path.join(workspace, fc)
        print 'No Dataset. FC, %s' % path

    # Print list of Tables
    print '\n\nTables: '
    for table in tables:
        path = os.path.join(workspace, table)
        print 'No Dataset.  TABLE, %s' % path


#-------------------------------------------------------------------------------
#                                 Run MAIN function
if __name__ == '__main__':
    main()
