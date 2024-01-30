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
    x1 = pd.read_excel(directoryName + '/forBot_FacultyAvailabilitySurvey.xlsx', engine='openpyxl')


    #print(x1)
    facultyList_df = x1[['Name','W','Max number of students', 'Campus Zone']]
    #facultyList = facultyList_df['First Name'] + ' ' + facultyList_df['Last Name']
    facultyList = facultyList_df['Name']
    print(facultyList_df)
    for iFaculty in range(len(facultyList)):
        facultyList[iFaculty] = facultyList[iFaculty].lstrip().rstrip()

    print(facultyList) # note these are e-mails right now. Need to manually change to names.

    stringOfAvailableSlots = x1['Please select the time slots you are available to interview prospective students.']

    stringOfAvailableSlots_all = '2/5 - 1:00 - 1:40 pm;2/5 - 1:45 - 2:15 pm;2/5 - 2:30 - 3:00 pm;2/5 - 3:15 - 3:45 pm;2/5 - 4:00 - 4:30 pm;2/6 - 1:00 - 1:30 pm;2/6 - 1:45 - 2:15 pm;2/6 - 2:30 - 3:00 pm;2/6 - 3:15 - 3:45 pm;'
    stringOfAvailableSlots_all_with_transit = '2/5 - 1:00 - 1:45 pm;2/5 - 1:45 - 2:30 pm;2/5 - 2:30 - 3:15 pm;2/5 - 3:15 - 4:00 pm;2/5 - 4:00 - 4:45 pm;2/6 - 1:00 - 1:45 pm;2/6 - 1:45 - 2:30 pm;2/6 - 2:30 - 3:15 pm;2/6 - 3:15 - 4:00 pm;'
    slots = stringOfAvailableSlots_all.split(';')
    slots_with_transit = stringOfAvailableSlots_all_with_transit.split(';')
    tmp = []
    for slot in slots:
        slot = slot.lstrip()
        tmp.append(slot)
    slots = tmp
    slots.pop()

    tmp = []
    for slot in slots_with_transit:
        slot = slot.lstrip()
        tmp.append(slot)
    slots_with_transit = tmp
    slots_with_transit.pop()

    #print(slots)

    # Make availability matrix, one column (faculty) at a time
    availabilityMatrix = np.zeros((len(slots), len(facultyList)))
    for iFaculty in range(len(x1)):
        #print(stringOfAvailableSlots[iFaculty])
        for iSlot in range(len(slots)):
            availability_test = stringOfAvailableSlots[iFaculty].find(slots[iSlot]) + stringOfAvailableSlots[iFaculty].find(slots_with_transit[iSlot]) > -2
            #print(slots[iSlot] + ' aka ' + slots_with_transit[iSlot] + ' Bool:' + str(availability_test)) 
            if availability_test:
                availabilityMatrix[iSlot,iFaculty] = 1
        # print(facultyList[iFaculty])
        # print(availabilityMatrix[:,iFaculty])
        # print(stringOfAvailableBigSlots[iFaculty])

    #print(availabilityMatrix)

    # make dataframe for export
    # put in alphabetical by last name

    facultyList_LastNameFirst = []
    for facultyName in facultyList:
        indivNames = facultyName.split(' ')
        facultyList_LastNameFirst.append(' '.join(reversed(indivNames))) 
    availabilityMatrixDataFrame = pd.DataFrame(data=availabilityMatrix,index=slots, columns=facultyList_LastNameFirst)    
    availabilityMatrixDataFrame.sort_index(axis=1, inplace=True) 

    facultyList = []
    for facultyName_LastNameFirst in availabilityMatrixDataFrame.columns:
        indivNames = facultyName_LastNameFirst.split(' ')
        facultyList.append(' '.join(reversed(indivNames))) 
    availabilityMatrixDataFrame.columns = facultyList
    print(facultyList)


    # facultyLastNames = []
    # for iFaculty in range(len(facultyList)):
    #     facultyLastNames.append(facultyList[iFaculty].split(' ')[-1])
    # facultyList_df['Last name'] = facultyLastNames
    # facultyList_df.sort_values(by=['Last name'], inplace=True)
    # print(facultyList_df)

    # write to excel file
    availabilityMatrixDataFrame.fillna(0).to_excel(directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx', engine='openpyxl')


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = '/Volumes/Carrot/Dropbox/science/service/MCSB/Admissions/2024Entry/03RecruitmentVisit/2024RealData' # EDIT FOLDERNAME HERE
    #FOLDERNAME = 'SampleData_RealAnon'
    translateFacultyAvailability(FOLDERNAME)
