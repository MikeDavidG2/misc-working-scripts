#-------------------------------------------------------------------------------
# Name:        MXD_to_PDF.py
# Purpose:
"""This script takes all of the MXD's that are in a folder ('ws' variable)
and searches the MXD's based on the 'file_search_variable'.
Any MXD's that satisfy the search will have a PDF generated for it
and saved to the out_folder variable.
"""
#
# Author:      mgrue
#
# Created:     16/11/2016
# Copyright:   (c) mgrue 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import arcpy, os

#-------------------------------------------------------------------------------
#                      Variables that WILL change

# What folder contains the MXD's you want to export to a PDF?
arcpy.env.workspace = ws = raw_input('Which folder has the files you want to export to a PDF?\n ')

# What search parameters do you want?
file_search_variable = raw_input('What do you want your search parameters to be (i.e. "*.mxd")?\n ')

# See if the user wants to put the PDF's into a 'PDF' folder in the directory that contains the MXD's
default_pdf_loc = ws + '\\pdf'
response = raw_input('Do you want to put the PDF files in:\n  "%s"? (y/n): ' % default_pdf_loc)

if response == 'y': # User wants to put files into default location
    if os.path.exists(default_pdf_loc):  # Check to see if the directory exists
        pass
    else:
        # Need to create the directory
        os.mkdir(default_pdf_loc)

    out_folder = default_pdf_loc

# The user wants to specify their own folder
else:
    # What folder do you want the PDF's to go into?
    out_folder = raw_input('What folder do you want to put the PDFs into?:\n ')


#-------------------------------------------------------------------------------
#                      Variables that MAY change


data_frame = 'PAGE_LAYOUT'
df_export_width = 640
df_export_height = 480
resolution = 300
image_quality = 'BEST'

# Can also use 'CMYK'
colorspace = 'RGB'
compress_vectors = True
image_compression = 'ADAPTIVE'
picture_symbol = 'RASTERIZE_BITMAP'
convert_markers = False
embed_fonts = True

#Can also use 'LAYERS_AND_ATTRIBUTES' or 'NONE'
layers_attributes = 'LAYERS_ONLY'
georef_info = True
jpeg_compression_quality = 80

#-------------------------------------------------------------------------------
#                      Variables that SHOULDN'T change

mxd_list = arcpy.ListFiles(file_search_variable)
success = True
arcpy.env.overwriteOutput = True

#-------------------------------------------------------------------------------
#**********************    Start FUNCTIONS    **********************************
#-------------------------------------------------------------------------------

def check_if_want_to_export(mxd_list_def):

    #---------------------------------------------------------------------------
    # Let the user know how many (and which) files will be processed
    #  with the current settings
    print '\n\nThe files that will be processed are:'
    total_files_to_process = 0
    for mxd_file in mxd_list_def:
        print mxd_file
        total_files_to_process += 1
    print '\nThere are: %s files to export to PDF.\n' % total_files_to_process

    #---------------------------------------------------------------------------
    # Confirm that user wants to export these files to PDF
    continue_script_def = raw_input('Do you want to export the above listed files to PDF? (y/n): ')
    return continue_script_def

#-------------------------------------------------------------------------------

def exportToPDF(mxd_def):

    print 'Exporting MXD: ' + mxd_def

    # Set variables that depend on the passed in parameter
    current_mxd = ws + '\\' + mxd_def
    map_document = arcpy.mapping.MapDocument(current_mxd)
    out_pdf = out_folder + '\\' + mxd_def[:-4] + ".pdf"

    arcpy.mapping.ExportToPDF (map_document, out_pdf, data_frame,
                               df_export_width, df_export_height,
                               resolution, image_quality, colorspace,
                               compress_vectors, image_compression,
                               picture_symbol, convert_markers,
                               embed_fonts, layers_attributes, georef_info,
                               jpeg_compression_quality)


#-------------------------------------------------------------------------------
#**********************    Start MAIN    ***************************************
#-------------------------------------------------------------------------------

# Check to see if the user wants to continue after reviwing the list of
# files that will be exported to PDF
try:
    continue_script = check_if_want_to_export(mxd_list)

except Exception as e:
    print 'ERROR!!!'
    print '\nThere was an ERROR with \'check_if_want_to_export\' for: ' + mxd
    print str(e)
    success = False

# If user wants to export the files to PDF, run exportToPDF function
if continue_script == 'y':
    for mxd in mxd_list:
        try:

            #Process
            exportToPDF(mxd)

        except Exception as e:
            print 'ERROR!!!'
            print '\nThere was an ERROR with \'exportToPDF\' for: ' + mxd
            print str(e)
            success = False

else:
    print 'You chose NOT to export to PDF.'


#-------------------------------------------------------------------------------
#**********************     End MAIN     ***************************************
#-------------------------------------------------------------------------------

del mxd_list


# Print end of script statements
if success == True:
    print '\nSUCCESS! \n    MXD_to_PDF.py completed successfully.'

else:
    print 'ERROR \n    There was an error with the MXD_to_PDF.py'

raw_input("Press ENTER to continue...")
