def translateStudentRequests(directoryName):

    import pandas as pd

    from fuzzywuzzy import fuzz #this is used in fuzzy line comparison to fix typos in names
    from fuzzywuzzy import process

    # Read in student requests in comma-separated list form
    x1 = pd.read_excel(directoryName + '/forBot_StudentRequestList.xlsx')


    # Read in core faculty list
    xFaculty = pd.read_excel(directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx')
    print(xFaculty.index)

    facultyList = list(xFaculty.columns)
    facultyList.pop(0)
    print(facultyList)

    missingFacultyList = ['Nobody']

    # Uncomment for Excel file with student names split in two columns
    #studentNames = x1['Last name'] + ', ' + x1['First name']
    studentNames = x1['Student name']

    studentChoices_Clean = pd.DataFrame(index=studentNames, columns=['wngbngd', 'asterisk', 'Faculty names'])

    for iStudent in range(len(x1)):

        #thisStudentChoices = x1.iloc[iStudent]['Faculty names'].replace('\xa0', '').replace(', and ', ', ').replace(' and ', ', ').split(',')
        #print(x1.iloc[iStudent]['Faculty names'])
        if not isinstance(x1.iloc[iStudent]['Faculty names'],float):
            thisStudentChoices = x1.iloc[iStudent]['Faculty names'].split(',')
        else:
            thisStudentChoices = ["Nobody"]

        thisStudentChoices_Clean = list()
        for iFacultyName in range(len(thisStudentChoices)):
            facultyName = thisStudentChoices[iFacultyName].lstrip()
            fuzzyCompare = process.extractOne(facultyName,facultyList, scorer=fuzz.WRatio)

            if fuzzyCompare[1]<70:
                print("This faculty is requested but has not declared availability: " + facultyName)
                fuzzyCompare = process.extractOne(facultyName,missingFacultyList, scorer=fuzz.WRatio)
                if fuzzyCompare[1]<70:
                    missingFacultyList.append(facultyName)

            else:
                    facultyName = fuzzyCompare[0]

            thisStudentChoices_Clean.append(facultyName)

        #print(thisStudentChoices_Clean)
        studentChoices_Clean.iloc[iStudent]['Faculty names'] = thisStudentChoices_Clean

    # sort list by last name
    facultyListSorted = sorted(facultyList, key=lambda x: x.split(" ")[-1])
    facultyListSorted = facultyList#sorted(facultyList, key=lambda x: x.split(" ")[-1])


    # Turn student requests into matrix form
    recruitChoices = pd.DataFrame(columns=facultyListSorted, index=studentNames)

    for iStudent in range(len(x1)):
        for iFaculty in studentChoices_Clean.iloc[iStudent]['Faculty names']:
            recruitChoices.iloc[iStudent][iFaculty] = 1

    recruitChoices.fillna(0).to_excel(directoryName + '/forBot_StudentRequestsMatrix.xlsx')


    print("Let's bug these faculty:")
    missingFacultyListSorted = sorted(missingFacultyList, key=lambda x: x.split(" ")[-1])
    print(map(lambda a: str(a), missingFacultyListSorted))


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = '~/Dropbox/science/service/MCSB/Admissions/2022Entry/03RecruitmentVisit/Test_DataFrom2021' # EDIT FOLDERNAME HERE
    translateStudentRequests(FOLDERNAME)
