#-------------------------------------------------------------------------------
# Name:        List_Fields.py
""" Purpose:   The purpose of this script is to print out a list of fields in
the FC or Table specified in the 'FC_or_table' variable.
"""
# Author:      mgrue
#
# Created:     17/01/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import arcpy


# Change the below variable to print the fields at this table
# It should be a full path and FC or Table name
FC_or_table = r'Database Connections\AD@ATLANTIC@SDE.sde\SDE.SANGIS.ECO_VEGETATION_CN'



#-------------------------------------------------------------------------------
def main():

    fields = arcpy.ListFields(FC_or_table)

    print 'Getting the fields in:\n  %s:\n' % (FC_or_table)

    for field in fields:
        print field.name

    print '\n'

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

