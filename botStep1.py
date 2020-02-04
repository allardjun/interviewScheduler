###############################################################################

# Make a folder. All xlsx files will go into this folder.
#
# Make a file forBotStudentRequests in which the first column is the student names,
# and second column is a list, separated by commas, of the faculty they requested.
#
# Run botStep1.py

# Get folder name.
# Reads in folder/forBot_CoreFaculty.xlsx
# Reads in folder/forBot_StudentRequests.xlsx

# Produces folder/forBot_FacultyAttributes.xlsx
# Produces folder/forBot_FacultyAvailabilityMatrix.xlsx
# Produces folder/forBot_StudentRequestMatrix.pickle

# Open folder/forBot_FacultyAttribues.xlsx and fill in gender of faculty.
# Open folder/forBot_FacultyAvailabilityMatrix.xlsx. Make first column the timeslots.
# Fill in folder/faculty availability as zeros (unavailable) and ones (available).
#
# Run botStep2.py

# Reads in folder/forBot_FacultyAttributes.xlsx
# Reads in folder/forBot_FacultyAvailabilityMatrix.xlsx
# Reads in folder/forBot_StudentRequestMatrix.pickle

# Produces folder/fromBot_FacultySchedules.xlsx
# Produces folder/fromBot_StudentSchedules.xlsx
###############################################################################




## ----- Inputs ------

# -- Get folder name --

directoryName = 'Example3_2020Entry'


# -- Read core faculty list and gender --
dfCoreFaculty = pd.read_excel('forBot_FacultyAttributes.xlsx', index_col=0).fillna(0).transpose()

# -- Read student requests --

translateStudentRequests

# -- Create full faculty list, core faculty status and core gender --

# -- Save faculty list and partial attributes to file --

# -- Create student request matrix --

# -- Save student request matrix to file --
