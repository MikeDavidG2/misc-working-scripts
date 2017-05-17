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
FC_or_table = r'E:\SAN DIEGO\GIS\Historic_Addresses.shp'

# Decide if you want the list returned as it is ordered in ArcCatalog or in alphabetical order
alpha_or_as_ordered = 'alpha'

#-------------------------------------------------------------------------------
def main():

    fields = arcpy.ListFields(FC_or_table)

    print 'Getting the fields in:\n  %s:\n' % (FC_or_table)

    # Print as ordered in ArcCatalog
    if alpha_or_as_ordered == 'as_ordered':
        for field in fields:
            print field.name

    # Print in alphabetical order
    elif alpha_or_as_ordered == 'alpha':
        f_list = []
        for field in fields:
            f_list.append(field.name)

        f_list.sort()

        for field in f_list:
            print field

    print '\n'

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

