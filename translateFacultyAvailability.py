# Part of interviewSchedule.py, for scheduling interviews between prospective grad students and PIs
# MCSB UCI Jun Allard mcsb.uci.edu, created 2020
# 
# Takes survey output from the faculty survey (not sure where it came from) in FacultyAvailabilitySurvey xlsx spreadsheet 
# returns a facultyRequestMatrix xlsx spreadsheet suitable for input into makeSchedule.py
# SLOTS must be hand-coded because of the clunky way they were returned by the survey app.

def translateFacultyAvailability(directoryName):

    import pandas as pd
    import numpy as np
    from fuzzywuzzy import fuzz #this is used in fuzzy line comparison to fix typos in names
    from fuzzywuzzy import process

    # Read in student requests in comma-separated list form
    x1 = pd.read_excel(directoryName + '/forBot_FacultyAvailabilitySurvey.xlsx')

    #print(x1)
    facultyList_df = x1[['Name','W','Max number of students']]
    facultyList = facultyList_df['Name']
    #print(facutlyList_df)
    for iFaculty in range(len(facultyList)):
        facultyList[iFaculty] = facultyList[iFaculty].lstrip().rstrip()

    print(facultyList) # note these are e-mails right now. Need to manually change to names.

    stringOfAvailableBigSlots = x1['I am available to interview students during the following time slots: ']

    # bigSlots = list()
    # for iFaculty in range(len(x1)):
    #     listOfAvailableBigSlots = stringOfAvailableBigSlots[iFaculty].split(';')
    #     for bigSlot in listOfAvailableBigSlots:
    #         bigSlot = bigSlot.lstrip()
    #         if bigSlot not in bigSlots:
    #             bigSlots.append(bigSlot)
    # bigSlots.sort()
    # bigSlots.pop(0)

    # -this is a hack and will need to be fixed either in Python or the survey!
    bigSlots = list()
    stringOfAvailableBigSlots_all = '2/7 12 - 1 PM;2/7 1 - 2 PM;2/7 2 - 3 PM;2/7 3 - 4 PM;2/7 4 - 5 PM;2/8 12 - 1 PM;2/8 1 - 2 PM;2/8 2 - 3 PM;2/8 3 - 4 PM;2/8 4 - 5 PM;'
    listOfAvailableBigSlots = stringOfAvailableBigSlots_all.split(';')
    for bigSlot in listOfAvailableBigSlots:
             bigSlot = bigSlot.lstrip()
             if bigSlot not in bigSlots:
                 bigSlots.append(bigSlot)
    bigSlots.pop()

    print(bigSlots)
      
    slots = list()
    for iBigSlot in bigSlots:
        slots.append(iBigSlot + ' :00')
        slots.append(iBigSlot + ' :30')


    # Make availability matrix, one column (faculty) at a time
    availabilityMatrix = np.zeros((len(slots), len(facultyList)))
    for iFaculty in range(len(x1)):
        for iBigSlot in range(len(bigSlots)):
            if bigSlots[iBigSlot] in stringOfAvailableBigSlots[iFaculty].lstrip().split(';'):
                availabilityMatrix[2*iBigSlot+0,iFaculty] = 1
                availabilityMatrix[2*iBigSlot+1,iFaculty] = 1
        # print(facultyList[iFaculty])
        # print(availabilityMatrix[:,iFaculty])
        # print(stringOfAvailableBigSlots[iFaculty])

    print(availabilityMatrix)

    # make dataframe for export
    # put in alphabetical by last name

    facultyList_LastNameFirst = []
    for facultyName in facultyList:
        indivNames = facultyName.split(' ')
        facultyList_LastNameFirst.append(' '.join(reversed(indivNames))) 
    availabilityMatrixDataFrame = pd.DataFrame(data=availabilityMatrix,index=slots, columns=facultyList_LastNameFirst)    
    availabilityMatrixDataFrame.sort_index(axis=1, inplace=True) 
    facultyList_sorted = sorted(facultyList, key=lambda x: x.split(" ")[-1])
    availabilityMatrixDataFrame.columns = facultyList_sorted
    print(facultyList_LastNameFirst)


    # facultyLastNames = []
    # for iFaculty in range(len(facultyList)):
    #     facultyLastNames.append(facultyList[iFaculty].split(' ')[-1])
    # facultyList_df['Last name'] = facultyLastNames
    # facultyList_df.sort_values(by=['Last name'], inplace=True)
    # print(facultyList_df)

    # write to excel file
    availabilityMatrixDataFrame.fillna(0).to_excel(directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx')


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    #FOLDERNAME = '~/Dropbox/science/service/MCSB/Admissions/2022Entry/03RecruitmentVisit/2022RealData_01290600' # EDIT FOLDERNAME HERE
    FOLDERNAME = 'SampleData_RealAnon'
    translateFacultyAvailability(FOLDERNAME)
