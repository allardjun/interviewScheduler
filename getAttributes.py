def getAttributes(directoryName):

    import numpy as np
    import pandas as pd

    ## ----- Inputs ------

    # -- Read faculty attributes --
    dfFacultyAttributesUnsorted = pd.read_excel('forBot_FacultyAttributes.xlsx', index_col=0).fillna(0).transpose()

    # sort by core vs noncore
    dfFacultyAttributesUnsorted_Core = dfFacultyAttributesUnsorted[dfFacultyAttributesUnsorted['Core'] == 1]
    dfFacultyAttributesUnsorted_Noncore = dfFacultyAttributesUnsorted[dfFacultyAttributesUnsorted['Core'] != 1]
    numCore = len(dfFacultyAttributesUnsorted_Core.index)
    numNoncore = len(dfFacultyAttributesUnsorted_Noncore.index)
    dfFacultyAttributes = pd.concat([dfFacultyAttributesUnsorted_Core, dfFacultyAttributesUnsorted_Noncore])

    facultyNames = list(dfFacultyAttributes.index)

    boolFemaleFaculty = list(dfFacultyAttributes["Female"] == 1)

    facultyFemaleList = np.nonzero(boolFemaleFaculty)[0]
    facultyFemaleSet = set(facultyFemaleList)

    # -- Read faculty availability --
    dfFacultyAvailabilityUnsorted = pd.read_excel('forBot_FacultyAvailabilityMatrix.xlsx', index_col=0).fillna(0).transpose()

    # sort by core vs noncore
    dfFacultyAvailabilityUnsorted_Core = dfFacultyAvailabilityUnsorted[dfFacultyAttributesUnsorted['Core'] == 1]
    dfFacultyAvailabilityUnsorted_Noncore = dfFacultyAvailabilityUnsorted[dfFacultyAttributesUnsorted['Core'] != 1]
    dfFacultyAvailability = pd.concat(
        [dfFacultyAvailabilityUnsorted_Core, dfFacultyAvailabilityUnsorted_Noncore]).transpose()

    boolFacultyAvailability = np.nan_to_num(dfFacultyAvailability.to_numpy())
    timeslotNames = dfFacultyAvailability.index
    if not all(dfFacultyAvailability.columns == facultyNames):
        print('The faculty names in the xlsx files do not match.')

    numTimeslots = len(timeslotNames)

    # -- Read student requests --

    dfStudentRequestsUnsorted = pd.read_excel('forBot_StudentRequestsMatrix.xlsx', index_col=0).fillna(0).transpose()

    # sort by core vs noncore
    dfStudentRequestsUnsorted_Core = dfStudentRequestsUnsorted[dfFacultyAttributesUnsorted['Core'] == 1]
    dfStudentRequestsUnsorted_Noncore = dfStudentRequestsUnsorted[dfFacultyAttributesUnsorted['Core'] != 1]
    dfStudentRequests = pd.concat([dfStudentRequestsUnsorted_Core, dfStudentRequestsUnsorted_Noncore]).transpose()

    boolStudentRequests = np.nan_to_num(dfStudentRequests.to_numpy())
    studentNames = dfStudentRequests.index
    if not all(dfStudentRequests.columns == facultyNames):
        print('The faculty names in the xlsx files do not match.')

    numStudents = len(studentNames)

    # -- Read student attributes --

    dfStudentAttributes = pd.read_excel('forBot_StudentAttributes.xlsx', index_col=0)

    if not all(dfStudentRequests.index == studentNames):
        print('The student names in the xlsx files do not match.')

    boolAsterisk = list(dfStudentAttributes['Asterisk'] == 1)
    numAsterisks = boolAsterisk.count(1)
    studentAsteriskList = np.nonzero(boolAsterisk)[0]

    boolFemaleStudent = list(dfStudentAttributes.iloc[:, 1] == 1)
    numFemaleStudents = boolFemaleStudent.count(1)
    studentFemaleList = np.nonzero(boolFemaleStudent)[0]

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    getAttributes('Example3_2020Entry')
