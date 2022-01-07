def translateFacultyAvailability(directoryName):


    import pandas as pd
    import numpy as np
    from fuzzywuzzy import fuzz #this is used in fuzzy line comparison to fix typos in names
    from fuzzywuzzy import process

    # Read in student requests in comma-separated list form
    x1 = pd.read_excel(directoryName + '/forBot_FacultyAvailabilitySurvey.xlsx')

    facultyList = x1['Name']
    print(facultyList) # note these are e-mails

    stringOfAvailableBigSlots = x1['I am available to interview students during the following time slots: ']

    bigSlots = list()
    for iFaculty in range(len(x1)):
        listOfAvailableBigSlots = stringOfAvailableBigSlots[iFaculty].split(';')
        for bigSlot in listOfAvailableBigSlots:
            if bigSlot not in bigSlots:
                bigSlots.append(bigSlot)
    bigSlots.sort()
    bigSlots.pop(0)

    print(bigSlots)
      
    slots = list()
    for iBigSlot in bigSlots:
        slots.append(iBigSlot + ' :00')
        slots.append(iBigSlot + ' :30')


    # Make availability matrix, one column (faculty) at a time
    availabilityMatrix = np.zeros((len(slots), len(facultyList)))
    for iFaculty in range(len(x1)):
        for iBigSlot in range(len(bigSlots)):
            if bigSlots[iBigSlot] in stringOfAvailableBigSlots[iFaculty].split(';'):
                availabilityMatrix[2*iBigSlot-1,iFaculty] = 1
                availabilityMatrix[2*iBigSlot-0,iFaculty] = 1
    
    print(availabilityMatrix)

    # make dataframe for export
    availabilityMatrixDataFrame = pd.DataFrame(data=availabilityMatrix,index=slots, columns=facultyList)    

    # write to excel file
    availabilityMatrixDataFrame.fillna(0).to_excel(directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx')


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = '~/Dropbox/science/service/MCSB/Admissions/2022Entry/03RecruitmentVisit/Test_DataFrom2021' # EDIT FOLDERNAME HERE
    translateFacultyAvailability(FOLDERNAME)
