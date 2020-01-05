import pandas as pd

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Read in student requests in comma-separated list form
file = 'Faculty_Choices.xlsx'
x1 = pd.read_excel(file)

facultyList = list()

studentNames = x1['Last name'] + ', ' + x1['First name']

studentChoices_Clean = pd.DataFrame(index=studentNames, columns=['Faculty names'])

for iStudent in range(len(x1)):

    thisStudentChoices = x1.iloc[iStudent]['Faculty choices'].replace('\xa0', '').replace(', and ', ', ').replace(' and ', ', ').split(',')

    thisStudentChoices_Clean = list()
    for iFacultyName in range(len(thisStudentChoices)):
        if len(facultyList)>1:
            facultyName = thisStudentChoices[iFacultyName].lstrip()
            fuzzyCompare = process.extractOne(facultyName,facultyList, scorer=fuzz.WRatio)
            if fuzzyCompare[1]<70:
                facultyList.append(facultyName)
            else:
                facultyName = fuzzyCompare[0]
        else:
            facultyName = thisStudentChoices[iFacultyName].lstrip()
            facultyList.append(facultyName)

        thisStudentChoices_Clean.append(facultyName)

    #print(thisStudentChoices_Clean)
    studentChoices_Clean.iloc[iStudent]['Faculty names'] = thisStudentChoices_Clean

# sort list by last name
facultyListSorted = sorted(facultyList, key=lambda x: x.split(" ")[-1])


# Turn student requests into matrix form
recruitChoices = pd.DataFrame(columns=facultyListSorted, index=studentNames)

for iStudent in range(len(x1)):
    for iFaculty in studentChoices_Clean.iloc[iStudent]['Faculty names']:
        recruitChoices.iloc[iStudent][iFaculty] = 1

recruitChoices.fillna(0).to_excel('forBot_StudentRequests.xlsx')
