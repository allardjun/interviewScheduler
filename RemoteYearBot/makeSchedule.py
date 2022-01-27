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
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    # ---------------- OPTIONS AND PARAMETERS -------------------------------

    # uncomment for repeatable runs
    if len(sys.argv)>1:
        mySeed = int(sys.argv[1])
        subdirectoryName = '/' + sys.argv[1]
        os.system("mkdir " + directoryName + subdirectoryName)
    else:
        mySeed = np.random.randint(40)
    np.random.seed(mySeed)
    print("mySeed=" + str(mySeed))

    visualize = 1  # whether or not to create graphic showing simulated annealing
    if visualize:
        listOfTargets = []

    ntmax = int(4e4) # int(2e4)  # total number of annealing timesteps to run. 4e4 takes about 2min CPU time.

    # relative importances of the targets
    alpha = {
        'Timezone': 2**5,
        'Gender': 2**5,
        'Fullness': 2**2,
        'Requests': 2**4,
        'AsteriskFullness': 0,
        'AsteriskRequests': 2**7,
        'FacultyFullness' : 2**7,
        'StudentsCriticallyLow': 2**7
    }

    tooManyStudentsToAFaculty = 8  # try to make sure each faculty meets no more than this many students
    criticalNumberOfInterviews = 5  # try to make sure each students meets at least this many faculty


    # timezones
    slotsInTimezone = {
        'EST':(0,1,2,3,10,11,12,13),
        'PST':(2,3,4,5,6,7,12,13,14,15,16),
        'AP':(7,8,9,17,18,19),
        'India':()
    }
    # day
    slotsInDay = {
        'Mon':range(0,9),
        'Tue':range(10,19),
    }

    # Temperature function aka Annealing function.
    annealingPrefactor = sum(alpha.values())

    def kBT(ntAnneal):
        return annealingPrefactor * np.power(1 - ntAnneal / float(ntmax+2), 6)

    # ---------------- READ INPUT FILES -------------------------------------
    # --------------- Read faculty attributes and availability

    dfFacultyAvailability = pd.read_excel(
        directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx', index_col=0).fillna(0)

    dfFacultySurvey = pd.read_excel(directoryName + '/forBot_FacultySurvey.xlsx', index_col=0).fillna(0)

    dfFacultyAttributes = dfFacultySurvey[['Name','W','Max number of students']].reset_index()
    facultyList = list(dfFacultyAttributes['Name'])
  
    facultyLastNames = []
    for iFaculty in range(len(facultyList)):
        facultyLastNames.append(facultyList[iFaculty].split(' ')[-1])
    dfFacultyAttributes['Last name'] = facultyLastNames
    dfFacultyAttributes.sort_values(by=['Last name'], inplace=True)
    #print(dfFacultyAttributes)

    #dfFacultyAvailability.drop(dfFacultyAvailability.head(2).index, inplace=True)
    boolFacultyAvailability = np.nan_to_num(dfFacultyAvailability.to_numpy())

    facultyNames = list(dfFacultyAvailability.columns)
    numFaculty = len(facultyNames)

    boolWomenFaculty = list(dfFacultyAttributes["W"] == 1)
    facultyWomenList = np.nonzero(boolWomenFaculty)[0]
    facultyWomenSet = set(facultyWomenList)

    maxNumberOfMeetings = list(dfFacultyAttributes['Max number of students'])
    maxNumberOfMeetings[:] = [tooManyStudentsToAFaculty if (x==0 or x>tooManyStudentsToAFaculty) else x for x in maxNumberOfMeetings]

    timeslotNames = dfFacultyAvailability.index
    numTimeslots = len(timeslotNames)

    # --------------- Get student requests
    dfStudentRequests = pd.read_excel(
        directoryName + '/forBot_StudentRequestsMatrix.xlsx', index_col=0).fillna(0)

    boolStudentRequests = np.nan_to_num(dfStudentRequests.to_numpy())
    studentNames = dfStudentRequests.index
    studentNamesList = list(studentNames)
    numStudents = len(studentNames)

    # --------------- Read student attributes
    dfStudentAttributes = pd.read_excel(
        directoryName + '/forBot_StudentRequestList.xlsx', index_col=0)
    if not all(dfStudentRequests.index == studentNames):
        # this should always pass, since the above file was made automatically
        print('The student names in the xlsx files do not match.')

    boolAsterisk = list(dfStudentAttributes['Asterisk'] == 1)
    numAsterisks = boolAsterisk.count(1)
    studentAsteriskList = np.nonzero(boolAsterisk)[0]

    boolGenderedStudent = list(dfStudentAttributes['W'] == 1)
    numGenderedStudents = boolGenderedStudent.count(1)
    studentGenderedList = np.nonzero(boolGenderedStudent)[0]

    timezone = dfStudentAttributes['Timezone']


    slotsForStudent = []
    for iStudent in range(numStudents):
        slotsForThisStudent = set()
        for day in ('Mon','Tue'):
            #print(iStudent)
            #print(day)
            #if dfStudentAttributes.iloc[iStudent].loc[day]==1:
            #    slotsForThisStudent = slotsForThisStudent | set(slotsInDay[day])
            slotsForThisStudent = slotsForThisStudent | set(slotsInDay[day]) # just use this line if everyone is here for both days. Otherwise use the two lines above.
        slotsForThisStudent = slotsForThisStudent & set(slotsInTimezone[timezone[iStudent]])
        slotsForStudent.append(list(slotsForThisStudent))

    # --------------- Special accommodations setup
    # blank for now!

    # ---------------- METROPOLIS GO! ---------------------------------------
    x = -1 * np.ones((numTimeslots, numFaculty))  # faculty schedule
    y = -1 * np.ones((numTimeslots, numStudents))  # student schedule

    xPropose = np.copy(x)
    yPropose = np.copy(y)
    xMin = np.copy(x)
    yMin = np.copy(y)

    proposalTargets = Targets()

    E = np.Inf
    EMin = np.Inf

    for nt in range(ntmax):

        # --------------- create proposal
        xPropose[:] = x
        yPropose[:] = y

        hardConstraintSatisfied = 0
        while not hardConstraintSatisfied:
            # --------------- single element change of core faculty schedule
            # --------------- pick a random slot in x (faculty schedule) and put a random student in it
            facultyAvailableNow = 0
            newStudent = 0
            timezoneSatisfied = 0
            while not facultyAvailableNow or not newStudent or not timezoneSatisfied:
                iFaculty = np.random.randint(numFaculty)
                iTimeslot = np.random.randint(numTimeslots)
                facultyAvailableNow = boolFacultyAvailability[iTimeslot, iFaculty]
                if facultyAvailableNow:
                    iStudent = np.random.randint(numStudents)
                    if iStudent not in xPropose[:, iFaculty]:
                        newStudent = 1
                        if iTimeslot in slotsForStudent[iStudent]:
                            timezoneSatisfied = 1
            xPropose[iTimeslot, iFaculty] = iStudent

            # --------------- Special accommodations: students with partial schedules
            # Nothing here yet!

            # --------------- eliminate student double bookings ("clones") and generate student schedules
            for iStudent in range(numStudents):
                for jTimeslot in range(numTimeslots):
                    clones = list(np.nonzero(xPropose[jTimeslot, :] == iStudent))[0]
                    if len(clones) == 0:
                        yPropose[jTimeslot, iStudent] = -1
                    elif len(clones) == 1:
                        yPropose[jTimeslot, iStudent] = clones[0]
                    else:
                        pickFaculty = np.random.choice(clones)
                        xPropose[jTimeslot, clones] = -1
                        xPropose[jTimeslot, pickFaculty] = iStudent
                        yPropose[jTimeslot, iStudent] = pickFaculty

            # --------------- Impose hard constraints (besides no clones)
            # --------------- Impose other special accomodations
            # Nothing here yet!
            hardConstraintSatisfied = 1

        # --------------- Compute targets

        # TARGET: Asterisk students get requested faculty
        proposalTargets.FractionOfAsteriskRequestSatisfied["min"] = 1
        fractionOfAsteriskRequestSatisfied_total = 0
        for iiStudent in range(numAsterisks):
            iStudent = studentAsteriskList[iiStudent]
            fractionOfAsteriskRequestSatisfied = len(set(np.where(boolStudentRequests[iStudent, :] == 1)[0]) & set(
                yPropose[:, iStudent])) / float(np.count_nonzero(boolStudentRequests[iStudent, :] == 1)+0.01)
            fractionOfAsteriskRequestSatisfied_total = fractionOfAsteriskRequestSatisfied_total + fractionOfAsteriskRequestSatisfied
            if proposalTargets.FractionOfAsteriskRequestSatisfied["min"] > fractionOfAsteriskRequestSatisfied:
                proposalTargets.FractionOfAsteriskRequestSatisfied["min"] = fractionOfAsteriskRequestSatisfied
        proposalTargets.FractionOfAsteriskRequestSatisfied["mean"] = fractionOfAsteriskRequestSatisfied_total/float(numAsterisks)


        # TARGET: Asterisk students get full schedules
        fractionAsteriskFull = sum(yPropose[:, studentAsteriskList] != -1) / float(numTimeslots)
        proposalTargets.FractionAsteriskFull["min"] = min(fractionAsteriskFull)
        proposalTargets.FractionAsteriskFull["mean"] = sum(fractionAsteriskFull) / float(numAsterisks)

        # TARGET: All students get requested faculty
        proposalTargets.FractionOfRequestSatisfied["min"] = 1
        fractionOfRequestSatisfied_total = 0
        for iStudent in range(numStudents):
            if np.count_nonzero(boolStudentRequests[iStudent, :] == 1) > 0:
                fractionOfRequestSatisfied = len(set(np.where(boolStudentRequests[iStudent, :] == 1)[0]) & set(
                    yPropose[:, iStudent])) / float(np.count_nonzero(boolStudentRequests[iStudent, :] == 1))
            else:
                fractionOfRequestSatisfied = 1
            fractionOfRequestSatisfied_total = fractionOfRequestSatisfied_total + fractionOfRequestSatisfied
            if proposalTargets.FractionOfRequestSatisfied["min"] > fractionOfRequestSatisfied:
                proposalTargets.FractionOfRequestSatisfied["min"] = fractionOfRequestSatisfied
        proposalTargets.FractionOfRequestSatisfied["mean"] = fractionOfRequestSatisfied_total/float(numStudents)

        # TARGET: All students get full schedules
        # np.delete(yPropose,jStudent,1) # TODO Modify to account for students without full schedules.
        yProposeFulltime = yPropose
        fractionFull = sum(yProposeFulltime != -1) / float(numTimeslots)
        proposalTargets.FractionFull["mean"] = sum(fractionFull)/float(numStudents)
        proposalTargets.FractionFull["min"] = min(fractionFull)

        # TARGET: Student should meet at least a set number of faculty
        proposalTargets.numStudentsCriticallyLow = sum(
            fractionFull <= criticalNumberOfInterviews/float(numTimeslots))

        # TARGET: Students should meet in their own timezone block
        proposalTargets.numberTimezoneViolations = 0

        # TARGET: Gendered students meet women faculty
        numMeetingWomen = 0
        for iiStudent in range(numGenderedStudents):
            numMeetingWomen += any(set(yPropose[:,studentGenderedList[iiStudent]]) & facultyWomenSet)
        proposalTargets.fractionGenderedMeeting = numMeetingWomen / float(numGenderedStudents)

        # TARGET: Make sure no faculty gets more than 9 students
        proposalTargets.facultyExcessMeetings = 0
        for iFaculty in range(numFaculty):
            numMeetings = numTimeslots - sum(xPropose[:, iFaculty] == -1)
            if numMeetings > maxNumberOfMeetings[iFaculty]:#tooManyStudentsToAFaculty:
                proposalTargets.facultyExcessMeetings += numMeetings - maxNumberOfMeetings[iFaculty]

        # --------------- Boltzmann test
        EPropose = - (
            alpha['Timezone'] * proposalTargets.numberTimezoneViolations
            + alpha['Gender'] * proposalTargets.fractionGenderedMeeting
            - alpha['FacultyFullness'] * proposalTargets.facultyExcessMeetings
            - alpha['StudentsCriticallyLow'] * proposalTargets.numStudentsCriticallyLow
            + alpha['AsteriskRequests'] * (10*proposalTargets.FractionOfAsteriskRequestSatisfied["min"]
                                            + proposalTargets.FractionOfAsteriskRequestSatisfied["mean"] )
            + alpha['AsteriskFullness'] * (10*proposalTargets.FractionAsteriskFull["min"]
                                            + proposalTargets.FractionAsteriskFull["mean"] )
            + alpha['Fullness'] * (10*proposalTargets.FractionFull["min"]
                                    + proposalTargets.FractionFull["mean"] )
            + alpha['Requests'] * (10*proposalTargets.FractionOfRequestSatisfied["min"]
                                    + proposalTargets.FractionOfRequestSatisfied["mean"] )
        )

        # Boltzmann test
        # Do it as two if statements to avoid runtime overflow.
        if EPropose < E or (np.random.rand() < np.exp(-(EPropose - E) / kBT(nt))):
            E = EPropose
            x[:] = xPropose
            y[:] = yPropose

        # --------------- Min test
        if EPropose < EMin:
            EMin = EPropose
            xMin[:] = xPropose
            yMin[:] = yPropose

            minTargets = proposalTargets.copy()

        if visualize:
            proposalTargets.E = EPropose
            listOfTargets.append(proposalTargets.copy())

    # finished annealing
    x[:] = xMin
    y[:] = yMin

    # ---------------- EXPORT TO SPREADSHEETS -----------------------------
    if 1:
        # --------------- All in one file, one sheet -----------------------
        # output faculty schedules with names
        xNames = np.empty((numTimeslots, numFaculty), dtype='object')
        for iFaculty in range(numFaculty):
            for iTimeslot in range(numTimeslots):
                if x[iTimeslot, iFaculty] == -1:
                    if boolFacultyAvailability[iTimeslot, iFaculty] == 0:
                        xNames[iTimeslot, iFaculty] = "..."
                    else:
                        xNames[iTimeslot, iFaculty] = "open"
                else:
                    xNames[iTimeslot, iFaculty] = studentNames[int(x[iTimeslot, iFaculty])]
        pd.DataFrame(data=xNames, index=timeslotNames, columns=facultyNames).to_excel(
            directoryName + subdirectoryName + '/fromBot_FacultySchedules.xlsx')

        # output student schedules with names
        yNames = np.empty((numTimeslots, numStudents), dtype='object')
        for iStudent in range(numStudents):
            for iTimeslot in range(numTimeslots):
                if y[iTimeslot, iStudent] == -1:
                    yNames[iTimeslot, iStudent] = "..."
                else:
                    yNames[iTimeslot, iStudent] = facultyNames[int(y[iTimeslot, iStudent])]
        pd.DataFrame(data=yNames, index=timeslotNames, columns=studentNames).to_excel(
            directoryName + subdirectoryName + '/fromBot_StudentSchedules.xlsx')

    if 1:
        # --------------- Different sheets -----------------------
        writer = pd.ExcelWriter(directoryName + subdirectoryName + '/fromBot_FacultySchedules_1SheetEach.xlsx', engine='xlsxwriter')
        # output faculty schedules with names
        for iFaculty in range(numFaculty):
            xNames = np.empty((numTimeslots, 1), dtype='object')
            nonEmpty = 0
            for iTimeslot in range(numTimeslots):
                if x[iTimeslot, iFaculty] == -1:
                    if boolFacultyAvailability[iTimeslot, iFaculty] == 0:
                        xNames[iTimeslot] = "..."
                    else:
                        xNames[iTimeslot] = "open"
                else:
                    xNames[iTimeslot] = studentNames[int(x[iTimeslot, iFaculty])]
                    nonEmpty = 1
            if nonEmpty == 1:
                sheetName=facultyNames[iFaculty].replace(" ", "")
                pd.DataFrame(data=xNames, index=timeslotNames, columns=[facultyNames[iFaculty]]
                    ).to_excel(writer,sheet_name=sheetName)
                writer.sheets[sheetName].set_column('A:A', 35)
                writer.sheets[sheetName].set_column('B:B', 30)
        writer.save()

        writer = pd.ExcelWriter(directoryName + subdirectoryName + '/fromBot_StudentSchedules_1SheetEach.xlsx', engine='xlsxwriter')
        # output student schedules with names
        for iStudent in range(numStudents):
            yNames = np.empty((numTimeslots, 2), dtype='object')
            for iTimeslot in range(numTimeslots):
                if y[iTimeslot, iStudent] == -1:
                    yNames[iTimeslot,0] = "..."
                else:
                    yNames[iTimeslot,0] = facultyNames[int(y[iTimeslot, iStudent])]
                    yNames[iTimeslot,1] = dfFacultyAttributes.iloc[int(y[iTimeslot, iStudent]),0]
            sheetName = studentNames[iStudent].replace(" ", "").replace("(", "").replace(")", "")
            pd.DataFrame(data=yNames, index=timeslotNames, columns=[studentNames[iStudent], "Location"]
                ).to_excel(writer,sheet_name=sheetName)
            writer.sheets[sheetName].set_column('A:A', 35)
            writer.sheets[sheetName].set_column('B:C', 30)
        writer.save()

    # ---------------- REPORTING - HOW'D WE DO? -----------------------------

    for i, iTarget in enumerate(vars(minTargets).items(),start=1):

        if isinstance(iTarget[1],dict): # if it's a target with a min and a mean
            print('%s = on average %3.0f%%, at worst %3.0f%%' % (iTarget[0], 100*getattr(minTargets,iTarget[0])['mean'], 100*getattr(minTargets,iTarget[0])['min']))
        else:
            print('%s = %3.2f' % (iTarget[0], getattr(minTargets,iTarget[0])))


    # ---------------- VISUALIZE ANNEALING ----------------------------------
    if visualize:
        fig = plt.figure(figsize=(18, 16))

        numberOfPlots = len(vars(proposalTargets))

        ntToPlot = range(ntmax)

        for i, iTarget in enumerate(vars(proposalTargets).items(),start=1):

            if isinstance(iTarget[1],dict): # if it's a target with a min and a mean
                ax = fig.add_subplot(numberOfPlots, 1, i)
                ax.title.set_text(iTarget[0])
                for nt in ntToPlot[::100]:
                    plt.plot(nt,getattr(listOfTargets[nt],iTarget[0])['min'], 'xr')
                    plt.plot(nt,getattr(listOfTargets[nt],iTarget[0])['mean'], 'ob')
            else:
                ax = fig.add_subplot(numberOfPlots, 1, i)
                ax.title.set_text(iTarget[0])
                for nt in ntToPlot[::100]:
                    plt.plot(nt,getattr(listOfTargets[nt],iTarget[0]), '+k')

        plt.show()

class Targets:
    def __init__(self):
        self.E = 0
        self.numberTimezoneViolations = 0
        self.fractionGenderedMeeting = 0
        self.facultyExcessMeetings = 0
        self.numStudentsCriticallyLow = 0
        self.FractionAsteriskFull = {'min':0, 'mean':0}
        self.FractionOfAsteriskRequestSatisfied = {'min':0, 'mean':0}
        self.FractionFull= {'min':0, 'mean':0}
        self.FractionOfRequestSatisfied = {'min':0, 'mean':0}

    def copy(self):
        targetCopy = Targets()
        for iTargetName, iTargetValue in vars(self).items():
            if isinstance(iTargetValue,dict):
                setattr(targetCopy,iTargetName,{'min':iTargetValue['min'], 'mean':iTargetValue['mean']})
            else:
                setattr(targetCopy,iTargetName,iTargetValue)
        return targetCopy


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = '~/Dropbox/science/service/MCSB/Admissions/2022Entry/03RecruitmentVisit/Test_DataFrom2022'  # EDIT FOLDERNAME HERE
    makeSchedule(FOLDERNAME)
