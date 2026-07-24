# Part of interviewSchedule.py, for scheduling interviews between prospective grad students and PIs
# MCSB UCI Jun Allard mcsb.uci.edu, created 2020
# 
# Takes studentRequestList xlsx spreadsheet (see format of sample), 
# returns a studentRequestMatrix xlsx spreadsheet suitable for input into makeSchedule.py

def translateStudentRequests(directoryName):

    import pandas as pd

    from rapidfuzz import fuzz, process  # fuzzy comparison to fix typos in names

    # Read in student requests in comma-separated list form
    x1 = pd.read_excel(directoryName + '/forBot_StudentRequestList.xlsx')




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



    studentChoices_Clean = list()

    for iStudent in range(len(x1)):

        print(x1.iloc[iStudent]['Faculty 1'])
        if not isinstance(x1.iloc[iStudent]['Faculty 1'],float):

            row = x1.iloc[iStudent]
            thisStudentChoices = [row[f'Faculty {i}'] for i in range(1, 7) if pd.notna(row[f'Faculty {i}'])]

        else:
            thisStudentChoices = ["Nobody"]
        print(thisStudentChoices)
        print("Here")

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
                    missingFacultyCounts[missingFacultyList.index(fuzzyCompare[0])] = missingFacultyCounts[missingFacultyList.index(fuzzyCompare[0])]+1

            else:
                facultyName = fuzzyCompare[0]

            thisStudentChoices_Clean.append(facultyName)

        print(thisStudentChoices_Clean)
        studentChoices_Clean.append(thisStudentChoices_Clean)

    # sort list by last name
    facultyList_LastNameFirst = []
    for facultyName in facultyList:
        indivNames = facultyName.split(' ')
        facultyList_LastNameFirst.append(' '.join(reversed(indivNames))) 
    facultyList_LastNameFirst_Sorted = sorted(facultyList_LastNameFirst)
    facultyList_Sorted = []
    for facultyName in facultyList_LastNameFirst_Sorted:
        indivNames = facultyName.split(' ')
        facultyList_Sorted.append(' '.join(reversed(indivNames))) 

    print("facultyList_Sorted:")
    print(facultyList_Sorted)

    # Turn student requests into matrix form
    studentChoices_matrix = pd.DataFrame(columns=facultyList_Sorted, index=studentNames)

    print("studentChoices_Clean:")
    print(studentChoices_Clean)

    print(studentChoices_matrix)

    for iStudent in range(len(x1)):
        for iFaculty in studentChoices_Clean[iStudent]:
            print(f"iStudent={iStudent}, iFaculty={iFaculty}, ", end="")
            if iFaculty in facultyList_Sorted:
                print("scheduled")
                studentChoices_matrix.loc[studentNames[iStudent],iFaculty] = 1
            else:
                print("not scheduled")

    print(studentChoices_matrix)


    studentChoices_matrix.fillna(0).to_excel(directoryName + '/forBot_StudentRequestsMatrix.xlsx')


    # FACULTY ENTICER GENERATOR
    print("Let's bug these faculty:")
    missingFacultyList_FirstName = [faculty.split(" ")[0] for faculty in missingFacultyList]
    df_missing_faculty = pd.DataFrame(list(zip(missingFacultyList, missingFacultyList_FirstName, missingFacultyCounts)), columns=['Faculty name', 'First name', 'Number of requests'])
    df_missing_faculty = df_missing_faculty.sort_values(by=['Number of requests'], ascending=False)

    print(df_missing_faculty)

    df_missing_faculty.to_excel(directoryName + '/fromBot_MIAFaculty.xlsx')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Translate the student request list into a request matrix. '
                    'Reads/writes forBot_*.xlsx in the given data folder.')
    parser.add_argument('folder',
                        help='folder containing the forBot_*.xlsx input files')
    args = parser.parse_args()
    translateStudentRequests(args.folder)
