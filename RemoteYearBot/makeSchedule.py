def makeSchedule(directoryName):

    # Outline of this function
    # ---------------- DEPENDENCIES -----------------------------------------

    # ---------------- OPTIONS AND PARAMETERS -------------------------------

    # ---------------- READ INPUT FILES -------------------------------------
    # --------------- Read faculty attributes
    # --------------- Get student requests
    # --------------- Read student attributes
    # --------------- Special accommodations setup

    # ---------------- METROPOLIS GO! ---------------------------------------
    # --------------- create proposal
    # --------------- single element change of core faculty schedule
    # --------------- pick a random slot in x (faculty schedule) and put a random student in it
    # --------------- Special accommodations: students with partial schedules
    # --------------- attempt single element change of non-core faculty schedule
    # --------------- pick a random slot in x and put a student(who requested this faculty) in it
    # --------------- eliminate student double bookings ("clones") and generate student schedules
    # --------------- hard constraints
    # --------------- Impose other special accomodations
    # --------------- Compute targets
    # --------------- Boltzmann test
    # --------------- Min test

    # ---------------- EXPORT TO SPREADSHEETS -----------------------------

    # ---------------- REPORTING - HOW'D WE DO? -----------------------------
    # ---------------- VISUALIZE ANNEALING ----------------------------------

    # ---------------- DEPENDENCIES -----------------------------------------
    # Before using, you need to pip install all of these.
    import xlsxwriter
    import sys
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    # ---------------- OPTIONS AND PARAMETERS -------------------------------

    ntmax = int(10)#int(2e4)  # total number of annealing timesteps to run. 4e4 takes about 2min CPU time.

    # relative importances of the targets
    alpha = {
        'Timezone': 2**5,
        'Gender': 2**5,
        'Fullness': 2**2,
        'Requests': 2**4,
        'AsteriskFullness': 0,
        'AsteriskRequests': 2**7
    }
    tooManyStudentsToAFaculty = 9

    # Temperature function aka Annealing function.
    annealingPrefactor = sum(alpha.values())

    def kBT(ntAnneal):
        return annealingPrefactor * np.power(1 - ntAnneal / float(ntmax+2), 6)

    # ---------------- READ INPUT FILES -------------------------------------
    # --------------- Read faculty attributes and availability

    dfFacultyAvailability = pd.read_excel(
        directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx', index_col=0).fillna(0)

    dfFacultyAttributes = dfFacultyAvailability.head(2).transpose()
    print(dfFacultyAttributes)

    dfFacultyAvailability.drop(dfFacultyAvailability.head(2).index, inplace=True)
    print(dfFacultyAvailability)
    boolFacultyAvailability = np.nan_to_num(dfFacultyAvailability.to_numpy())

    facultyNames = list(dfFacultyAvailability.columns)
    print(facultyNames)
    numFaculty = len(facultyNames)

    boolWomenFaculty = list(dfFacultyAttributes["W"] == 1)
    facultyWomenList = np.nonzero(boolWomenFaculty)[0]
    facultyWomenSet = set(facultyWomenList)

    timeslotNames = dfFacultyAvailability.index
    numTimeslots = len(timeslotNames)
    print(timeslotNames)

    # --------------- Get student requests
    dfStudentRequests = pd.read_excel(
        directoryName + '/forBot_StudentRequestsMatrix.xlsx', index_col=0).fillna(0)

    boolStudentRequests = np.nan_to_num(dfStudentRequests.to_numpy())
    studentNames = dfStudentRequests.index
    studentNamesList = list(studentNames)
    numStudents = len(studentNames)
    print(studentNames)
    print(studentNamesList)

    # --------------- Read student attributes
    dfStudentAttributes = pd.read_excel(directoryName + '/forBot_StudentRequestList.xlsx', index_col=0)
    if not all(dfStudentRequests.index == studentNames):
        print('The student names in the xlsx files do not match.') # this should always pass, since the above file was made automatically

    boolAsterisk = list(dfStudentAttributes['Asterisk'] == 1)
    numAsterisks = boolAsterisk.count(1)
    studentAsteriskList = np.nonzero(boolAsterisk)[0]
    print(studentAsteriskList)

    boolGenderedStudent = list(dfStudentAttributes['W'] == 1)
    numGenderedStudents = boolGenderedStudent.count(1)
    studentGenderedList = np.nonzero(boolGenderedStudent)[0]
    print(studentGenderedList)

    # --------------- Special accommodations setup
    # blank for now!

    # ---------------- METROPOLIS GO! ---------------------------------------
    x = -1 * np.ones((numTimeslots, numFaculty))  # faculty schedule
    y = -1 * np.ones((numTimeslots, numStudents))  # student schedule

    xPropose = np.copy(x)
    yPropose = np.copy(y)
    xMin = np.copy(x)
    yMin = np.copy(y)

    E = np.Inf
    EMin = np.Inf

    for nt in range(ntmax):

        # --------------- create proposal
        xPropose[:] = x
        yPropose[:] = y

        # --------------- single element change of core faculty schedule
        # --------------- pick a random slot in x (faculty schedule) and put a random student in it
        facultyAvailableNow = 0
        newStudent = 0
        while not facultyAvailableNow or not newStudent:
            iFaculty = np.random.randint(numFaculty)
            iTimeslot = np.random.randint(numTimeslots)
            facultyAvailableNow = boolFacultyAvailability[iTimeslot, iFaculty]
            if facultyAvailableNow:
                iStudent = np.random.randint(numStudents)
                if iStudent not in xPropose[:, iFaculty]:
                    newStudent = 1
        xPropose[iTimeslot, iFaculty] = iStudent

        # --------------- Special accommodations: students with partial schedules
        # Nothing here yet!

        # --------------- eliminate student double bookings ("clones") and generate student schedules
        for iStudent in range(numStudents):
            for iTimeslot in range(numTimeslots):
                clones = list(np.nonzero(xPropose[iTimeslot, :] == iStudent))[0]
                if len(clones) == 0:
                    yPropose[iTimeslot, iStudent] = -1
                elif len(clones) == 1:
                    yPropose[iTimeslot, iStudent] = clones[0]
                else:
                    pickFaculty = np.random.choice(clones)
                    xPropose[iTimeslot, clones] = -1
                    xPropose[iTimeslot, pickFaculty] = iStudent
                    yPropose[iTimeslot, iStudent] = pickFaculty

        # --------------- hard constraints (besides no clones)
        # Nothing here yet!

        # --------------- Impose other special accomodations
        # Nothing here yet!

        # --------------- Compute targets
        # Gendered students meet women faculty
        numMeetingWomen = 0
        for iiStudent in range(numGenderedStudents):
            numMeetingWomen += any(set(yPropose[:, studentGenderedList[iiStudent]]) & facultyWomenSet)
        fractionGenderedMeeting = numMeetingWomen / float(numGenderedStudents)

        # Asterisk students get requested faculty
        minFractionOfAsteriskRequestSatisfied = 1
        totalFractionOfAsteriskRequestSatisfied = 0
        for iiStudent in range(numAsterisks):
            iStudent = studentAsteriskList[iiStudent]

        fractionOfAsteriskRequestSatisfied = len(set(np.where(boolStudentRequests[iStudent, :] == 1)[0]) & set(yPropose[:, iStudent])) / float(np.count_nonzero(boolStudentRequests[iStudent, :] == 1))
        totalFractionOfAsteriskRequestSatisfied = totalFractionOfAsteriskRequestSatisfied + fractionOfAsteriskRequestSatisfied
        if minFractionOfAsteriskRequestSatisfied > fractionOfAsteriskRequestSatisfied:
            minFractionOfAsteriskRequestSatisfied = fractionOfAsteriskRequestSatisfied


        # Asterisk students get full schedules
        fractionAsteriskFull = sum(yPropose[:, studentAsteriskList] != -1) / float(numTimeslots)
        totalFractionAsteriskFull = sum(fractionAsteriskFull)
        minFractionAsteriskFull = min(fractionAsteriskFull)

        # All students get full schedules
        yProposeFulltime = yPropose#np.delete(yPropose,jStudent,1)
        fractionFull = sum(yProposeFulltime != -1) / float(numTimeslots)
        totalFractionFull = sum(fractionFull)
        minFractionFull = min(fractionFull)

        numFiveOrLess = sum(fractionFull <= 5.0/float(numTimeslots))
        #print(numFiveOrLess)

        # All students get requested faculty
        minFractionOfRequestSatisfied = 1
        totalFractionOfRequestSatisfied = 0
        for iStudent in range(numStudents):
            if np.count_nonzero(boolStudentRequests[iStudent, :] == 1) > 0:
                fractionOfRequestSatisfied = len(set(np.where(boolStudentRequests[iStudent, :] == 1)[0]) & set(yPropose[:, iStudent]) ) / float(np.count_nonzero(boolStudentRequests[iStudent, :] == 1))
            else:
                fractionOfRequestSatisfied = 1
            totalFractionOfRequestSatisfied = totalFractionOfRequestSatisfied + fractionOfRequestSatisfied
            if minFractionOfRequestSatisfied > fractionOfRequestSatisfied:
                minFractionOfRequestSatisfied = fractionOfRequestSatisfied

        # Make sure no faculty gets more than 9 students
        facultyMeetingTooManyStudents = 0
        for iFaculty in range(numFaculty):
            numMeetings = numTimeslots - sum(xPropose[:,iFaculty]==-1)
            if numMeetings > tooManyStudentsToAFaculty:
                facultyMeetingTooManyStudents += 1

        # --------------- Boltzmann test
        # --------------- Min test

        # ---------------- EXPORT TO SPREADSHEETS -----------------------------

        # ---------------- REPORTING - HOW'D WE DO? -----------------------------
        # ---------------- VISUALIZE ANNEALING ----------------------------------


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = 'SampleData_RealAnon2020'  # EDIT FOLDERNAME HERE
    makeSchedule(FOLDERNAME)
