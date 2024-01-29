# Part of interviewSchedule.py, for scheduling interviews between prospective grad students and PIs
# MCSB UCI Jun Allard mcsb.uci.edu, created 2020
# 
# Takes studentRequestList xlsx spreadsheet (see format of sample), 
# returns a studentRequestMatrix xlsx spreadsheet suitable for input into makeSchedule.py

def translateStudentRequests(directoryName):

    import pandas as pd

    from fuzzywuzzy import fuzz #this is used in fuzzy line comparison to fix typos in names
    from fuzzywuzzy import process

    # Read in student requests in comma-separated list form
    x1 = pd.read_excel(directoryName + '/forBot_StudentRequestList.xlsx')

    #x1['Faculty names'] = x1['Faculty requested']

    for iStudent in x1.index:
        x1['Faculty names'][iStudent] = str(x1['Faculty requested'][iStudent])#  + str(x1['Faculty suggestions'][iStudent]) 
    #x1['Faculty names'] = x1['Faculty requests'] #+ x1['Faculty suggestions']

    print(x1['Faculty names'])

    # Read in core faculty list
    xFaculty = pd.read_excel(directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx')
    print(xFaculty.index)

    facultyList = list(xFaculty.columns)
    facultyList.pop(0)
    print(facultyList)

    missingFacultyList = ['Nobody']
    missingFacultyCounts = []

    # Uncomment for Excel file with student names split in two columns
    studentNames = x1['Last Name'] + ', ' + x1['First Name']
    #studentNames = x1['Last Name']

    studentChoices_Clean = pd.DataFrame(index=studentNames, columns=['wngbngd', 'asterisk', 'Faculty requested', 'Faculty suggestions', 'Faculty names'])

    for iStudent in range(len(x1)):

        print(x1.iloc[iStudent]['Faculty names'])
        if not isinstance(x1.iloc[iStudent]['Faculty names'],float):
            thisStudentChoices = x1.iloc[iStudent]['Faculty names'].replace('\xa0', '').replace(', and ', ', ').replace(' and ', ', ').replace('Dr.', '').replace('Dr. ', '').replace('Professor ', '').replace('Prof.', '').replace('Prof. ', '').replace('.', '').split(',')
        else:
            thisStudentChoices = ["Nobody"]
        print(thisStudentChoices)

        thisStudentChoices_Clean = list()
        for iFacultyName in range(len(thisStudentChoices)):
            facultyName = thisStudentChoices[iFacultyName].lstrip()
            fuzzyCompare = process.extractOne(facultyName,facultyList, scorer=fuzz.WRatio)

            if fuzzyCompare[1]<70:
                print("This faculty is requested but has not declared availability: " + facultyName)
                fuzzyCompare = process.extractOne(facultyName,missingFacultyList, scorer=fuzz.WRatio)
                if fuzzyCompare[1]<70:
                    missingFacultyList.append(facultyName)
                    missingFacultyCounts.append(1)
                else:
                    #print(missingFacultyCounts)
                    #print(type(missingFacultyCounts))
                    #print(fuzzyCompare)
                    missingFacultyCounts[missingFacultyList.index(fuzzyCompare[0])] = missingFacultyCounts[missingFacultyList.index(fuzzyCompare[0])]+1

            else:
                    facultyName = fuzzyCompare[0]

            thisStudentChoices_Clean.append(facultyName)

        #print(thisStudentChoices_Clean)
        studentChoices_Clean.iloc[iStudent]['Faculty names'] = thisStudentChoices_Clean

    # sort list by last name
    #facultyListSorted = sorted(facultyList, key=lambda x: x.split(" ")[-1])
    #facultyListSorted = facultyList#sorted(facultyList, key=lambda x: x.split(" ")[-1])
    facultyList_LastNameFirst = []
    for facultyName in facultyList:
        indivNames = facultyName.split(' ')
        facultyList_LastNameFirst.append(' '.join(reversed(indivNames))) 
    facultyList_LastNameFirst_Sorted = sorted(facultyList_LastNameFirst)
    facultyList_Sorted = []
    for facultyName in facultyList_LastNameFirst_Sorted:
        indivNames = facultyName.split(' ')
        facultyList_Sorted.append(' '.join(reversed(indivNames))) 

    # Turn student requests into matrix form
    studentChoices_matrix = pd.DataFrame(columns=facultyList_Sorted, index=studentNames)

    for iStudent in range(len(x1)):
        for iFaculty in studentChoices_Clean.iloc[iStudent]['Faculty names']:
            studentChoices_matrix.iloc[iStudent][iFaculty] = 1

    studentChoices_matrix.fillna(0).to_excel(directoryName + '/forBot_StudentRequestsMatrix.xlsx')


    # FACULTY ENTICER GENERATOR
    print("Let's bug these faculty:")
    #print(missingFacultyList)
    #missingFacultyListSorted = sorted(missingFacultyList, key=lambda x: x.split(" ")[-1])
    #print(*missingFacultyListSorted, sep="\n")
    missingFacultyList_FirstName = [faculty.split(" ")[0] for faculty in missingFacultyList]
    df_missing_faculty = pd.DataFrame(list(zip(missingFacultyList, missingFacultyList_FirstName, missingFacultyCounts)), columns=['Faculty name', 'First name', 'Number of requests'])
    df_missing_faculty = df_missing_faculty.sort_values(by=['Number of requests'], ascending=False)

    #print("\n".join("{} {}".format(x, y) for x, y in zip(missingFacultyList, missingFacultyCounts)))
    print(df_missing_faculty)

    df_missing_faculty.to_excel(directoryName + '/fromBot_MIAFaculty.xlsx')

if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = '/Volumes/Carrot/Dropbox/science/service/MCSB/Admissions/2023Entry/03RecruitmentVisit/2023RealData' # EDIT FOLDERNAME HERE
    #FOLDERNAME = 'SampleData_RealAnon' # EDIT FOLDERNAME HERE
    translateStudentRequests(FOLDERNAME)
