"""This script was written by Gary Ross.  It is intended to aggregate the
Habitrak data on the P drive (located at: P:\habitrak\data\County of San Diego.mdb)
so that it mimics the schema on SDE (located at: SDE.SANGIS.ECO_MSCP_HABITRAK_CN)

You will need to confirm that the inputData and workspace are correct,
but otherwise the script shouldn't need ammending.
"""

import sys, string, os, time, math, ConfigParser
import arcpy
arcpy.env.overwriteOutput = True

#-------------------------------------------------------------------------------
#                               Set variables
# Location for Habitrak personal database
inputData = "P:\\habitrak\\data\\County of San Diego.mdb"

# Set folder structure inside the personal database
data = "Projects\\Projects"
gain = "Gain"
loss = "Loss"

# Location for a repository FGDB
workspace = "P:\\habitrak\\working\\workspace.gdb"

#-------------------------------------------------------------------------------

try:
    startTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print "\nHABITRAK UPDATE START TIME: " + str(startTime)

    arcpy.env.workspace = workspace

    # Copy dataset and tables
    arcpy.Copy_management(inputData + "\\" + data,"projects")
    arcpy.Copy_management(inputData + "\\" + gain,"gain")
    arcpy.Copy_management(inputData + "\\" + loss,"loss")
    print "Datasets copied..."


    # Add fields
    arcpy.AddField_management("projects","TRACKNO","TEXT","","",50)
    arcpy.AddField_management("projects","PROJTYPE","TEXT","","",50)
    arcpy.AddField_management("projects","PROJNAME","TEXT","","",100)
    arcpy.AddField_management("projects","APPLICANT","TEXT","","",100)
    arcpy.AddField_management("projects","ACTIVITY","TEXT","","",50)
    arcpy.AddField_management("projects","ACTIVITY_DATE","DATE")
    arcpy.AddField_management("projects","MGMTDESCRIP","TEXT","","",50,"Management Description")
    arcpy.AddField_management("projects","ACRES","DOUBLE",38,8)
    print "Fields added..."

    # Losses
    arcpy.MakeFeatureLayer_management("projects","prj_loss","\"TYPE\" = 2")
    arcpy.AddJoin_management("prj_loss","PROJECTID","loss","PROJECTID")
    arcpy.CalculateField_management("prj_loss","projects.TRACKNO","[loss.TRACKNO]")
    arcpy.CalculateField_management("prj_loss","projects.PROJTYPE","\"LOSS\"")
    arcpy.CalculateField_management("prj_loss","projects.PROJNAME","[loss.PROJECTNAME]")
    arcpy.CalculateField_management("prj_loss","projects.APPLICANT","[loss.APPLICANT]")
    arcpy.CalculateField_management("prj_loss","projects.ACTIVITY","[loss.ACTIVITY]")
    arcpy.CalculateField_management("prj_loss","projects.ACTIVITY_DATE","[loss.DATELOSS]")
    arcpy.CalculateField_management("prj_loss","projects.MGMTDESCRIP","[loss.ACTIVITYDESCRIP]")
    arcpy.RemoveJoin_management("prj_loss","loss")
    print "Loss information populated..."

    # Gains
    arcpy.MakeFeatureLayer_management("projects","prj_gain","\"TYPE\" = 1")
    arcpy.AddJoin_management("prj_gain","PROJECTID","gain","PROJECTID")
    arcpy.CalculateField_management("prj_gain","projects.TRACKNO","[gain.TRACKNO]")
    arcpy.CalculateField_management("prj_gain","projects.PROJTYPE","\"GAIN\"")
    arcpy.CalculateField_management("prj_gain","projects.PROJNAME","[gain.PROJECTNAME]")
    arcpy.CalculateField_management("prj_gain","projects.APPLICANT","[gain.APPLICANT]")
    arcpy.CalculateField_management("prj_gain","projects.ACTIVITY","[gain.CONSTYPE]")
    arcpy.CalculateField_management("prj_gain","projects.ACTIVITY_DATE","[gain.DATEGAIN]")
    arcpy.CalculateField_management("prj_gain","projects.MGMTDESCRIP","[gain.MGMTDESCRIP]")
    arcpy.RemoveJoin_management("prj_gain","gain")
    print "Gain information populated..."

    arcpy.MakeFeatureLayer_management("projects","prjlyr1","\"MGMTDESCRIP\" = '1' OR \"MGMTDESCRIP\" = '2' OR \"MGMTDESCRIP\" = '3' OR \"MGMTDESCRIP\" = '4' OR \"MGMTDESCRIP\" = '5' OR \"MGMTDESCRIP\" = '6'")
    arcpy.AddJoin_management("prjlyr1","MGMTDESCRIP","DOMAIN_MGMTRESP","VAL")
    arcpy.CalculateField_management("prjlyr1","projects.MGMTDESCRIP","[DOMAIN_MGMTRESP.DESCRIPTION]")
    arcpy.RemoveJoin_management("prjlyr1","DOMAIN_MGMTRESP")

    arcpy.MakeFeatureLayer_management("projects","prjlyr2","\"ACTIVITY\" <> '-1' AND \"ACTIVITY\" <> '0' AND \"PROJTYPE\" = 'LOSS'")
    arcpy.AddJoin_management("prjlyr2","ACTIVITY","DOMAIN_LACTIVITY","VAL")
    arcpy.CalculateField_management("prjlyr2","projects.ACTIVITY","[DOMAIN_LACTIVITY.DESCRIPTION]")
    arcpy.RemoveJoin_management("prjlyr2","DOMAIN_LACTIVITY")

    arcpy.MakeFeatureLayer_management("projects","prjlyr3","(\"ACTIVITY\" = '1' OR \"ACTIVITY\" = '2' OR \"ACTIVITY\" = '3' OR \"ACTIVITY\" = '4' OR \"ACTIVITY\" = '5' OR \"ACTIVITY\" = '6' OR \"ACTIVITY\" = '7' OR \"ACTIVITY\" = '8') AND \"PROJTYPE\" = 'GAIN'")
    arcpy.AddJoin_management("prjlyr3","ACTIVITY","DOMAIN_GACTIVITY","VAL")
    arcpy.CalculateField_management("prjlyr3","projects.ACTIVITY","[DOMAIN_GACTIVITY.DESCRIPTION]")
    arcpy.RemoveJoin_management("prjlyr3","DOMAIN_GACTIVITY")

    arcpy.Dissolve_management("projects","ECO_MSCP_HABITRAK_CN",
                              "TRACKNO;PROJTYPE;PROJNAME;APPLICANT;ACTIVITY;ACTIVITY_DATE;MGMTDESCRIP;ACRES")
    arcpy.CalculateField_management("ECO_MSCP_HABITRAK_CN","ACRES","[SHAPE_area] / 43560")

    print "\n" + str(workspace) + "\\ECO_MSCP_HABITRAK_CN has been updated..."
    print "Copy and update metadata and load into SDE"
    print "HABITRAK UPDATE END TIME: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

except:
    print ""
    print "AN ERROR HAS OCCURRED IN UPDATE_HABITRAK.PY (" + str(time.strftime("%Y%m%d %H:%M:%S", time.localtime())) + ")..."
    print ""
    print arcpy.GetMessages()