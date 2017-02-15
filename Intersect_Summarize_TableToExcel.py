"""
This script takes features to intersect and intersects them with an intersect_fc
The resulting dataset is put into the out_fgdb where it repairs the geometry
then creates a summary and then exports the summary to Excel.

It was used for a request from PDS Advanced Planning about PSR's and the frequency
with which a species should occur in a PSR.

The above project can be found in: 'P:\20160922_SpeciesWithPotentialToOccur'
"""
import arcpy
arcpy.env.overwriteOutput = True
#-------------------------------------------------------------------------
#                        Variables that may change

# Which FGDB contains the features you want to intersect?
in_fgdb = r'P:\mscp\covered_species\species_patches.gdb'

#Which FC do you want to target the intersection with (from the in_fgdb variable)
intersect_fc = r'P:\20160922_SpeciesWithPotentialToOccur\5694_SpeciesWithPotentialToOccur\v101\species.gdb\IntersectData\ChampagneGardens_PSR_Merge'

# Which FGDB do you want to put the intersected FCs?
out_fgdb = r'P:\20161007_SpeciesWithPotentialToOccur\Intersections.gdb'

# What do you want to append to the end of the intersected FCs?
append_to_fc = '_int_PSR'

# Where do you want the CSV files to go?
csv_loc = r'P:\20161007_SpeciesWithPotentialToOccur\CSVs'

#-------------------------------------------------------------------------
#                         Variables that shouldn't change

# Set a flag for success or not
success = True

# Get a list of feature classes in the in_fgdb
try:
    arcpy.env.workspace = in_fgdb
    listToIntersect = arcpy.ListFeatureClasses()
except Exception as e:
    print 'There was an ERROR with setting the workspace or listing the FCs:'
    print str(e)
    success = False



#-------------------------------------------------------------------------
#*******************       START FUNCTIONS  ******************************
#-------------------------------------------------------------------------
def intersect(featureClass):
    try:
        print '    Intersecting... '

        in_features = [featureClass, intersect_fc]
        out_feature_class = out_fgdb + '\\' + featureClass + append_to_fc
        join_attributes = 'ALL'
        cluster_tolerance = ''
        output_type = ''

        arcpy.Intersect_analysis (in_features, out_feature_class, join_attributes, cluster_tolerance, output_type)
        print '    Intersect complete!'
    except Exception as e:
        print 'There was an ERROR with intersect:'
        print str(e)
        success = False

#-------------------------------------------------------------------------
def repairGeom(featureClass):
    try:
        print '    Repairing Geometry...'

        in_features = featureClass
        delete_null = 'DELETE_NULL'

        arcpy.RepairGeometry_management (in_features, delete_null)

        print '    Repair complete!'

    except Exception as e:
        print 'There was an ERROR with repairGeom:'
        print str(e)
        success = False

#------------------------------------------------------------------------
def summarize(featureClass):
    try:
        print '    Summarizing...'

        in_table = featureClass
        out_table = out_fgdb + '\\' + fc + '_sum'
        statistics_fields = [["Shape_Area", "SUM"]]
        case_field = "LONGNAME"

        arcpy.Statistics_analysis (in_table, out_table, statistics_fields, case_field)

        print '    Summarizing complete!'

    except Exception as e:
        print 'There was an ERROR with summarize:'
        print str(e)
        success = False

#------------------------------------------------------------------------
def tableToExcel(table):
    try:
        print '    Exporting to .dbf'

        in_rows = table
        out_path = csv_loc
        out_name = fc + '.csv'
        where_clause = ''
        field_mapping = ''
        config_keyword = ''

        arcpy.TableToTable_conversion (in_rows, out_path, out_name, where_clause, field_mapping, config_keyword)

        print '    Exporting Complete!'

    except Exception as e:
        print 'There was an ERROR with tableToExcel:'
        print str(e)
        success = False

#-------------------------------------------------------------------------
#*******************       START MAIN       ******************************
#-------------------------------------------------------------------------
listToIntersect.sort()
for fc in listToIntersect:
    print fc
"""
if success == True:
    for fc in listToIntersect:
        print 'Processing: ' + fc

        intersect(fc)
        repairGeom(out_fgdb + '\\' + fc + '_int_PSR')
        summarize(out_fgdb + '\\' + fc + '_int_PSR')
        tableToExcel(out_fgdb + '\\' + fc + '_sum')

        print 'Finished processing!\n'
else:
    print 'MAIN not processed since there was an error above.'
"""
#-------------------------------------------------------------------------
#*******************       FINISH MAIN       ******************************
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#**************       PRINT FINAL STATEMENT       ************************
#-------------------------------------------------------------------------
if success == True:
    print '\nFinished SUCCESSFULLY'

else:
    print '\nERROR!!!'
    print 'There was an error with the script, please check for the error message above.'

