#-------------------------------------------------------------------------------
# Name:        Schema_Creation.py
# Purpose:     To create a schema using a CSV file.  You can find a TEMPLATE of
# The CSV file at U:\grue\Scripts\GitHub\Misc_Working_Scripts\Schema_Creation_Template.csv
#
# Author:      mgrue
#
# Created:     18/10/2017
# Copyright:   (c) mgrue 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import csv, arcpy, time
def main():

    # Set Only Variable you should need to change
    csv_with_schema = r"U:\yakos\hep_A\TEST\Sites_Schema_Collector.csv"


    #---------------------------------------------------------------------------
    # Run script
    added_fields = 0

    with open (csv_with_schema) as csv_file:
        readCSV = csv.reader(csv_file, delimiter = ',')

        row_num = 0
        for row in readCSV:
            if row_num > 0:
                in_table          = row[0]
                field_name        = row[1]
                field_type        = row[2]
                field_precision   = ''
                field_scale       = ''
                field_length      = row[3]
                field_alias       = row[4]
                field_is_nullable = 'NULLABLE'
                field_is_required = 'NON_REQUIRED'
                field_domain      = row[5]

                print 'To Feature Class: {}'.format(in_table)
                print '    Adding field: {}'.format(field_name)
                ##print '  With Precision: {}'.format(field_precision)  # These should always be blank if using a FGDB
                ##print '           Scale: {}'.format(field_scale)  # These should always be blank if using a FGDB
                print '          Length: {}'.format(field_length)
                print '           Alias: {}'.format(field_alias)
                print '        Nullable: {}'.format(field_is_nullable)
                print '        Required: {}'.format(field_is_required)
                print '          Domain: {}'.format(field_domain)


                try:
                    arcpy.AddField_management (in_table, field_name, field_type, field_precision, field_scale, field_length, field_alias, field_is_nullable, field_is_required, field_domain)
                    print 'Successfully added field'
                    added_fields += 1
                except Exception as e:
                    print 'ERROR!'
                    print arcpy.GetMessages()
                    print '-----'
                    print str(e)
            row_num += 1
            time.sleep(2)
            print '\n----------------------------------------------------------'

    #---------------------------------------------------------------------------
    # End of script reporting
    print 'Tried to add:       "{}" fields'.format(row_num-1)
    print 'Successfully added: "{}" fields'.format(added_fields)
    if row_num-1 != added_fields:
        print 'WARNING! You didn\'t add all fields.'



#-------------------------------------------------------------------------------
# Call main() function
if __name__ == '__main__':
    main()
