def makeSchedule(directoryName):

    import numpy as np
    import pandas as pd
    import xlsxwriter

    import sys

    import matplotlib.pyplot as plt

    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    # uncomment for repeatable runs
    #mySeed = np.random.randint(20)
    #np.random.seed(mySeed)
    #print("mySeed=" + str(mySeed))

    # parameters

    excelRow2Location = 1 # whether the second row of facultyAvailability contains the faculty office location

    visualize = 0  # whether or not to create graphic showing simulated annealing

    ntmax = int(2e4)  # int(2e4)  # total number of annealing timesteps to run. 4e4 takes about 2min CPU time.

    # relative importances of the targets
    alpha_Female = 2**5
    alpha_AsteriskMinRequests = 2**7
    alpha_AsteriskFull = 0#**3
    alpha_Full = 2**2
    alpha_minRequests = 2**4

    ## ----- Inputs ------

    # -- Read faculty availability --
    dfFacultyAvailabilityUnsorted = pd.read_excel(directoryName + '/forBot_FacultyAvailabilityMatrix.xlsx', index_col=0).fillna(0).transpose()

    # sort by core vs noncore
    dfFacultyAvailabilityUnsorted_Core = dfFacultyAvailabilityUnsorted#dfFacultyAvailabilityUnsorted[dfFacultyAttributesUnsorted['Core'] == 1]
    #dfFacultyAvailabilityUnsorted_Noncore = dfFacultyAvailabilityUnsorted[dfFacultyAttributesUnsorted['Core'] != 1]
    dfFacultyAvailability = dfFacultyAvailabilityUnsorted_Core.transpose()#pd.concat([dfFacultyAvailabilityUnsorted_Core, dfFacultyAvailabilityUnsorted_Noncore]).transpose()

    # remove first row, which contains gender
    if excelRow2Location==1:
        dfFacultyAvailability.drop(dfFacultyAvailability.head(1).index,inplace=True)

    # remove last row, which contains gender
    dfFacultyAvailability.drop(dfFacultyAvailability.tail(1).index,inplace=True)

    boolFacultyAvailability = np.nan_to_num(dfFacultyAvailability.to_numpy())
    timeslotNames = dfFacultyAvailability.index
    numTimeslots = len(timeslotNames)

    print(timeslotNames)
    #print(numTimeslots)

    facultyNames = list(dfFacultyAvailabilityUnsorted.index)

    numCore = len(facultyNames)
    numNoncore = 0

    # -- Read faculty attributes --
    dfFacultyAttributes = dfFacultyAvailabilityUnsorted_Core.transpose().tail(1).transpose()

    #print(dfFacultyAttributes)

    boolFemaleFaculty = list(dfFacultyAttributes["W"] == 1)

    facultyFemaleList = np.nonzero(boolFemaleFaculty)[0]
    facultyFemaleSet = set(facultyFemaleList)

    if excelRow2Location==1:
        dfFacultyLocations = dfFacultyAvailabilityUnsorted_Core.transpose().head(1).transpose()

    iArthur = facultyNames.index(process.extractOne("Lander",facultyNames, scorer=fuzz.WRatio)[0])

    # -- Read student requests --

    dfStudentRequestsUnsorted = pd.read_excel(directoryName + '/forBot_StudentRequestsMatrix.xlsx', index_col=0).fillna(0).transpose()

    # sort by core vs noncore
    dfStudentRequestsUnsorted_Core = dfStudentRequestsUnsorted#[dfFacultyAttributesUnsorted['Core'] == 1]
    #dfStudentRequestsUnsorted_Noncore = dfStudentRequestsUnsorted[dfFacultyAttributesUnsorted['Core'] != 1]
    dfStudentRequests = dfStudentRequestsUnsorted_Core.transpose()#pd.concat([dfStudentRequestsUnsorted_Core, dfStudentRequestsUnsorted_Noncore]).transpose()

    boolStudentRequests = np.nan_to_num(dfStudentRequests.to_numpy())
    studentNames = dfStudentRequests.index
    studentNamesList = list(studentNames)

    facultyNamesFromStudents = list(dfStudentRequests.columns)
    for ilist in range(len(facultyNamesFromStudents)):
        if not (facultyNamesFromStudents[ilist] == facultyNames[ilist]):
            print('The faculty names in the xlsx files do not match.')
            print(facultyNamesFromStudents[ilist])
            print(facultyNames[ilist])

    numStudents = len(studentNames)

    # -- Read student attributes --

    dfStudentAttributes = pd.read_excel(directoryName + '/forBot_StudentRequestList.xlsx', index_col=0)

    if not all(dfStudentRequests.index == studentNames):
        print('The student names in the xlsx files do not match.')

    boolAsterisk = list(dfStudentAttributes['Asterisk'] == 1)
    numAsterisks = boolAsterisk.count(1)
    studentAsteriskList = np.nonzero(boolAsterisk)[0]

    boolFemaleStudent = list(dfStudentAttributes['W'] == 1)
    numFemaleStudents = boolFemaleStudent.count(1)
    studentFemaleList = np.nonzero(boolFemaleStudent)[0]
    #print("Number of W students: " + str(numFemaleStudents))


    # --- SPECIAL ACCOMODATIONS ---
    # anything that is better outside the loop, like getting the index of the student
    jStudent = studentNamesList.index(process.extractOne("Nguyen",studentNamesList, scorer=fuzz.WRatio)[0])

    ## --- setup ----

    x = -1 * np.ones((numTimeslots, numCore + numNoncore))  # faculty schedule
    y = -1 * np.ones((numTimeslots, numStudents))  # student schedule

    xPropose = np.copy(x)
    yPropose = np.copy(y)
    xMin = np.copy(x)
    yMin = np.copy(y)

    E = np.Inf
    EMin = np.Inf

    # Temperature function aka Annealing function.
    def kBT(ntAnneal):
        return sum([alpha_Female, alpha_AsteriskMinRequests, alpha_AsteriskFull, alpha_Full, alpha_minRequests]) * \
            np.power(1 - ntAnneal / float(ntmax+2), 6)

    if (visualize):
        fractionFemaleMeeting_array                   = np.zeros((1, ntmax))
        minFractionOfAsteriskRequestSatisfied_array   = np.zeros((1, ntmax))
        totalFractionOfAsteriskRequestSatisfied_array = np.zeros((1, ntmax))
        minFractionAsteriskFull_array                 = np.zeros((1, ntmax))
        totalFractionAsteriskFull_array               = np.zeros((1, ntmax))
        minFractionFull_array                         = np.zeros((1, ntmax))
        totalFractionFull_array                       = np.zeros((1, ntmax))
        minFractionOfRequestSatisfied_array           = np.zeros((1, ntmax))
        totalFractionOfRequestSatisfied_array         = np.zeros((1, ntmax))
        E_array                                       = np.zeros((1, ntmax))

    #print(ntmax-numTimeslots*(numCore+numNoncore))

    ## Metropolis go!
    for nt in range(ntmax):

        # --- create proposal ---
        xPropose[:] = x
        yPropose[:] = y

        if np.random.rand() < numCore / float(numCore + numNoncore):  # single element change of core faculty schedule
            # pick a random slot in x and put a random student in it
            facultyAvailableNow = 0
            newStudent = 0
            while not facultyAvailableNow or not newStudent:
                iFaculty = np.random.randint(numCore)
                iTimeslot = np.random.randint(numTimeslots)
                facultyAvailableNow = boolFacultyAvailability[iTimeslot, iFaculty]
                if facultyAvailableNow:
                    iStudent = np.random.randint(numStudents)
                    #if iFaculty == 0:
                    #    print(xPropose[:, iFaculty])
                    #print(iStudent not in xPropose[:, iFaculty])
                    if iStudent not in xPropose[:, iFaculty]:
                        newStudent = 1

                # STUDENTS WITH PARTIAL SCHEDULES
                if 0:
                    if (iTimeslot>5 and iStudent == jStudent):
                        facultyAvailableNow = 0

            xPropose[iTimeslot, iFaculty] = iStudent

        else:  # attempt single element change of non-core faculty schedule
            # pick a random slot in x and put a student(who requested this faculty) in it
            facultyAvailableNow = 0
            newStudent = 0
            numAttemptsNonCore = 0
            while (not facultyAvailableNow or not newStudent) and numAttemptsNonCore < numNoncore * numStudents:
                iFaculty = np.random.randint(numNoncore) + numCore
                requestedBy = np.nonzero(boolStudentRequests[:, iFaculty])[0]

                if len(requestedBy) != 0:
                    iTimeslot = np.random.randint(numTimeslots)
                    facultyAvailableNow = boolFacultyAvailability[iTimeslot, iFaculty]

                    if facultyAvailableNow:
                        iStudent = requestedBy[np.random.randint(len(requestedBy))]
                        if iStudent not in xPropose[:, iFaculty]:
                            newStudent = 1

                numAttemptsNonCore += 1
            if numAttemptsNonCore < numNoncore * numStudents:
                xPropose[iTimeslot, iFaculty] = iStudent

        # eliminate student double bookings ("clones") and generate student schedules
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

        # ------ hard constraints -----

        if 0:
            # prevent conflict overlap in last 3 timeslots on Tuesday
            for iStudent in range(numStudents):
                if not(yPropose[numTimeslots-1,iStudent]==-1):
                    if not(yPropose[numTimeslots-2,iStudent]==-1):
                        if np.random.rand()<0.5:
                            clearMe=numTimeslots-1
                        else:
                            clearMe=numTimeslots-2
                        xPropose[clearMe,int(yPropose[clearMe,iStudent])]=-1
                        yPropose[clearMe,iStudent]=-1
            for iFaculty in range(numCore):
                if not(xPropose[numTimeslots-1,iFaculty]==-1):
                    if not(xPropose[numTimeslots-2,iFaculty]==-1):
                        if np.random.rand()<0.5:
                            clearMe=numTimeslots-1
                        else:
                            clearMe=numTimeslots-2
                        yPropose[clearMe,int(xPropose[clearMe,iFaculty])]=-1
                        xPropose[clearMe,iFaculty]=-1

            for iStudent in range(numStudents):
                if not(yPropose[numTimeslots-2,iStudent]==-1):
                    if not(yPropose[numTimeslots-3,iStudent]==-1):
                        if np.random.rand()<0.5:
                            clearMe=numTimeslots-2
                        else:
                            clearMe=numTimeslots-3
                        xPropose[clearMe,int(yPropose[clearMe,iStudent])]=-1
                        yPropose[clearMe,iStudent]=-1
            for iFaculty in range(numCore):
                if not(xPropose[numTimeslots-2,iFaculty]==-1):
                    if not(xPropose[numTimeslots-3,iFaculty]==-1):
                        if np.random.rand()<0.5:
                            clearMe=numTimeslots-2
                        else:
                            clearMe=numTimeslots-3
                        yPropose[clearMe,int(xPropose[clearMe,iFaculty])]=-1
                        xPropose[clearMe,iFaculty]=-1

        if 0:
            # Arthur needs 15 more minutes of sleep while partying in Spain while the rest of us work
            iStudentArthur245 = int(xPropose[2,iArthur])
             #print(iStudentArthur245)
            if (not (iStudentArthur245==-1)):
                #print("student " + str(yPropose[3,iStudentArthur245]))
                if (not (yPropose[3,iStudentArthur245] == -1)):
                    xPropose[3,int(yPropose[3,iStudentArthur245])] = -1
                    yPropose[3,iStudentArthur245] = -1

        # --- compute targets ---

        # Female + non-gender-binary/declared meet female faculty
        numMeetingFemale = 0
        for iiStudent in range(numFemaleStudents):
            numMeetingFemale += any(set(yPropose[:, studentFemaleList[iiStudent]]) & facultyFemaleSet)
        # finished loop through asterisk students
        fractionFemaleMeeting = numMeetingFemale / float(numFemaleStudents)

        # Asterisk students get requested faculty
        minFractionOfAsteriskRequestSatisfied = 1
        totalFractionOfAsteriskRequestSatisfied = 0
        for iiStudent in range(numAsterisks):
            iStudent = studentAsteriskList[iiStudent]

            fractionOfAsteriskRequestSatisfied = len(set(np.where(boolStudentRequests[iStudent, :] == 1)[0]) & set(yPropose[:, iStudent])) / float(np.count_nonzero(boolStudentRequests[iStudent, :] == 1))
            totalFractionOfAsteriskRequestSatisfied = totalFractionOfAsteriskRequestSatisfied + fractionOfAsteriskRequestSatisfied
            if minFractionOfAsteriskRequestSatisfied > fractionOfAsteriskRequestSatisfied:
                minFractionOfAsteriskRequestSatisfied = fractionOfAsteriskRequestSatisfied
        # finished loop through asterisk students

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
        # finished loop through all students


        # Make sure no faculty gets more than 9 students
        facultyMeetingTooManyStudents = 0
        for iFaculty in range(numCore+numNoncore):
            numMeetings = numTimeslots - sum(xPropose[:,iFaculty]==-1)
            if numMeetings > 9:
                facultyMeetingTooManyStudents += 1

        # TO DO?:Minimize walking between med campus and core campus

        # Compute objective function
        EPropose = - (alpha_Female * fractionFemaleMeeting
                      + alpha_AsteriskMinRequests * (  1*minFractionOfAsteriskRequestSatisfied + totalFractionOfAsteriskRequestSatisfied / float(numAsterisks))
                      + alpha_AsteriskFull        * ( 10*minFractionAsteriskFull + totalFractionAsteriskFull / float(numAsterisks))
                      + alpha_Full                * ( 10*minFractionFull + totalFractionFull / float(numStudents))
                      + alpha_minRequests         * ( 10*minFractionOfRequestSatisfied + totalFractionOfRequestSatisfied / float(numStudents))
                      - facultyMeetingTooManyStudents
                      - numFiveOrLess)

        # Boltzmann test
        # Do it as two if statements to avoid runtime overflow.
        if EPropose < E or (np.random.rand() < np.exp(-(EPropose - E) / kBT(nt))):
            E = EPropose
            x[:] = xPropose
            y[:] = yPropose

        # Min test
        if EPropose < EMin:
            EMin = EPropose
            xMin[:] = xPropose
            yMin[:] = yPropose

            fractionFemaleMeeting_min                   = fractionFemaleMeeting
            minFractionOfAsteriskRequestSatisfied_min   = minFractionOfAsteriskRequestSatisfied
            totalFractionOfAsteriskRequestSatisfied_min = totalFractionOfAsteriskRequestSatisfied
            minFractionAsteriskFull_min                 = minFractionAsteriskFull
            totalFractionAsteriskFull_min               = totalFractionAsteriskFull
            minFractionFull_min                         = minFractionFull
            totalFractionFull_min                       = totalFractionFull
            minFractionOfRequestSatisfied_min           = minFractionOfRequestSatisfied
            totalFractionOfRequestSatisfied_min         = totalFractionOfRequestSatisfied
            E_min = E


        if visualize:
            fractionFemaleMeeting_array[0, nt]                   = fractionFemaleMeeting
            minFractionOfAsteriskRequestSatisfied_array[0, nt]   = minFractionOfAsteriskRequestSatisfied
            totalFractionOfAsteriskRequestSatisfied_array[0, nt] = totalFractionOfAsteriskRequestSatisfied
            minFractionAsteriskFull_array[0, nt]                 = minFractionAsteriskFull
            totalFractionAsteriskFull_array[0, nt]               = totalFractionAsteriskFull
            minFractionFull_array[0, nt]                         = minFractionFull
            totalFractionFull_array[0, nt]                       = totalFractionFull
            minFractionOfRequestSatisfied_array[0, nt]           = minFractionOfRequestSatisfied
            totalFractionOfRequestSatisfied_array[0, nt]         = totalFractionOfRequestSatisfied
            E_array[0, nt] = E

    # finished annealing

    x[:] = xMin
    y[:] = yMin

    ## Reporting

    if (1):
        print('Percent of female+ngb/ngd students meeting a female faculty: %3.0f%%' %
              (100 * fractionFemaleMeeting_min))

        print('Percent of requests satisfied, for students on asterisk list: On average: %3.0f%%, at worst: %3.0f%%' %
              (100 * totalFractionOfAsteriskRequestSatisfied_min / float(numAsterisks),
               100 * minFractionOfAsteriskRequestSatisfied_min))

        print('Percent of requests satisfied, for all students: On average: %3.0f%%, at worst: %3.0f%%' %
              (100 * totalFractionOfRequestSatisfied_min / float(numStudents),
               100 * minFractionOfRequestSatisfied_min))

        print('Percent schedule full, for students on asterisk list: On average: %3.0f%%, at worst: %3.0f%%' %
              (100 * totalFractionAsteriskFull_min / float(numAsterisks),
               100 * minFractionAsteriskFull_min))

        print('Percent schedule full, for all students: On average: %3.0f%%, at worst: %3.0f%%' %
              (100 * totalFractionFull_min / float(numStudents),
               100 * minFractionFull_min))

        print("Number of faculty meeting more than 9 students: " + str(facultyMeetingTooManyStudents))

        print("Number of students meeting fewer than 6 faculty: " + str(numFiveOrLess))


    ## output

    if 1:
        # --------------- All in one file, one sheet -----------------------
        # output faculty schedules with names
        xNames = np.empty((numTimeslots, numCore + numNoncore), dtype='object')
        for iFaculty in range(numCore + numNoncore):
            for iTimeslot in range(numTimeslots):
                if x[iTimeslot, iFaculty] == -1:
                    if boolFacultyAvailability[iTimeslot, iFaculty] == 0:
                        xNames[iTimeslot, iFaculty] = "..."
                    else:
                        xNames[iTimeslot, iFaculty] = "open"
                else:
                    xNames[iTimeslot, iFaculty] = studentNames[x[iTimeslot, iFaculty]]
        pd.DataFrame(data=xNames, index=timeslotNames, columns=facultyNames).to_excel(
            directoryName + '/fromBot_FacultySchedules.xlsx')

        # output student schedules with names
        yNames = np.empty((numTimeslots, numStudents), dtype='object')
        for iStudent in range(numStudents):
            for iTimeslot in range(numTimeslots):
                if y[iTimeslot, iStudent] == -1:
                    yNames[iTimeslot, iStudent] = "..."
                else:
                    yNames[iTimeslot, iStudent] = facultyNames[int(y[iTimeslot, iStudent])]
        pd.DataFrame(data=yNames, index=timeslotNames, columns=studentNames).to_excel(
            directoryName + '/fromBot_StudentSchedules.xlsx')

    if 0:
        # --------------- Each a separate file -----------------------
        # output faculty schedules with names
        for iFaculty in range(numCore + numNoncore):
            xNames = np.empty((numTimeslots, 1), dtype='object')
            nonEmpty = 0
            for iTimeslot in range(numTimeslots):
                if x[iTimeslot, iFaculty] == -1:
                    if boolFacultyAvailability[iTimeslot, iFaculty] == 0:
                        xNames[iTimeslot] = "..."
                    else:
                        xNames[iTimeslot] = "open"
                else:
                    xNames[iTimeslot] = studentNames[x[iTimeslot, iFaculty]]
                    nonEmpty = 1
            if nonEmpty == 1:
                pd.DataFrame(data=xNames, index=timeslotNames, columns=[facultyNames[iFaculty]]
                    ).to_excel(directoryName + '/faculty_'
                    + facultyNames[iFaculty].replace(" ", "") + '.xlsx')

        # output student schedules with names
        for iStudent in range(numStudents):
            yNames = np.empty((numTimeslots, 1), dtype='object')
            for iTimeslot in range(numTimeslots):
                if y[iTimeslot, iStudent] == -1:
                    yNames[iTimeslot] = "..."
                else:
                    yNames[iTimeslot] = facultyNames[int(y[iTimeslot, iStudent])]
            pd.DataFrame(data=yNames, index=timeslotNames, columns=[studentNames[iStudent]]
                ).to_excel(directoryName + '/student_'
                + studentNames[iStudent].replace(" ", "").replace("(", "").replace(")", "") + '.xlsx')

    if 1:
        # --------------- Different sheets -----------------------
        writer = pd.ExcelWriter(directoryName + '/fromBot_FacultySchedules_1SheetEach.xlsx', engine='xlsxwriter')
        # output faculty schedules with names
        for iFaculty in range(numCore + numNoncore):
            xNames = np.empty((numTimeslots, 1), dtype='object')
            nonEmpty = 0
            for iTimeslot in range(numTimeslots):
                if x[iTimeslot, iFaculty] == -1:
                    if boolFacultyAvailability[iTimeslot, iFaculty] == 0:
                        xNames[iTimeslot] = "..."
                    else:
                        xNames[iTimeslot] = "open"
                else:
                    xNames[iTimeslot] = studentNames[x[iTimeslot, iFaculty]]
                    nonEmpty = 1
            if nonEmpty == 1:
                sheetName=facultyNames[iFaculty].replace(" ", "")
                pd.DataFrame(data=xNames, index=timeslotNames, columns=[facultyNames[iFaculty]]
                    ).to_excel(writer,sheet_name=sheetName)
                writer.sheets[sheetName].set_column('A:A', 35)
                writer.sheets[sheetName].set_column('B:B', 30)
        writer.save()

        writer = pd.ExcelWriter(directoryName + '/fromBot_StudentSchedules_1SheetEach.xlsx', engine='xlsxwriter')
        # output student schedules with names
        for iStudent in range(numStudents):
            yNames = np.empty((numTimeslots, 2), dtype='object')
            for iTimeslot in range(numTimeslots):
                if y[iTimeslot, iStudent] == -1:
                    yNames[iTimeslot,0] = "..."
                else:
                    yNames[iTimeslot,0] = facultyNames[int(y[iTimeslot, iStudent])]
                    yNames[iTimeslot,1] = dfFacultyLocations.iloc[int(y[iTimeslot, iStudent]),0]
            sheetName = studentNames[iStudent].replace(" ", "").replace("(", "").replace(")", "")
            pd.DataFrame(data=yNames, index=timeslotNames, columns=[studentNames[iStudent], "Location"]
                ).to_excel(writer,sheet_name=sheetName)
            writer.sheets[sheetName].set_column('A:A', 35)
            writer.sheets[sheetName].set_column('B:C', 30)
        writer.save()


    ## Visualize
    if visualize:
        fig = plt.figure(figsize=(18, 16))

        ax = fig.add_subplot(6, 1, 1)
        ax.set_ylim(0, 1)
        plt.plot(fractionFemaleMeeting_array[0, :], '+b')
        ax.set_ylabel("fractionFemaleMeeting_array")

        ax = fig.add_subplot(6, 1, 2)
        ax.set_ylim(0, 1)
        plt.plot(minFractionOfAsteriskRequestSatisfied_array[0, :], '+b')
        plt.plot(totalFractionOfAsteriskRequestSatisfied_array[0, :] / float(numAsterisks), 'or')
        ax.set_ylabel('fractionOfAsteriskRequestSatisfied_array')

        ax = fig.add_subplot(6, 1, 3)
        ax.set_ylim(0, 1)
        plt.plot(minFractionAsteriskFull_array[0, :], '+b')
        plt.plot(totalFractionAsteriskFull_array[0, :] / float(numAsterisks), 'or')
        ax.set_ylabel('FractionAsteriskFull')

        ax = fig.add_subplot(6, 1, 4)
        ax.set_ylim(0, 1)
        plt.plot(minFractionFull_array[0, :], '+b')
        plt.plot(totalFractionFull_array[0, :] / float(numStudents), 'or')
        ax.set_ylabel('FractionFull_array')

        ax = fig.add_subplot(6, 1, 5)
        ax.set_ylim(0, 1)
        plt.plot(minFractionOfRequestSatisfied_array[0, :], '+b')
        plt.plot(totalFractionOfRequestSatisfied_array[0, :] / float(numStudents), 'or')
        ax.set_ylabel('FractionOfRequestSatisfied_array')

        ax = fig.add_subplot(6, 1, 6)
        plt.plot(E_array[0, :], '+b')

        plt.show()


if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = 'SampleData_RealAnon2020' # EDIT FOLDERNAME HERE
    makeSchedule(FOLDERNAME)
