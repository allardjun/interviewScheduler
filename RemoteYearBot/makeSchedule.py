def makeSchedule(directoryName):


    ## Outline of this function
    ## ---------------- DEPENDENCIES -----------------------------------------

    ## ---------------- OPTIONS AND PARAMETERS -------------------------------

    ## ---------------- READ INPUT FILES -------------------------------------
    ### --------------- Read faculty attributes
    ### --------------- Get student requests
    ### --------------- Read student attributes
    ### --------------- Special accommodations setup

    ## ---------------- METROPOLIS GO! ---------------------------------------
    ### --------------- create proposal
    ### --------------- single element change of core faculty schedule
    ### --------------- pick a random slot in x (faculty schedule) and put a random student in it
    ### --------------- Special accommodations: students with partial schedules
    ### --------------- attempt single element change of non-core faculty schedule
    ### --------------- pick a random slot in x and put a student(who requested this faculty) in it
    ### --------------- eliminate student double bookings ("clones") and generate student schedules
    ### --------------- hard constraints
    ### --------------- Impose other special accomodations
    ### --------------- Compute targets
    ### --------------- Boltzmann test
    ### --------------- Min test

    ## ---------------- EXPORT TO SPREADSHEETS -----------------------------

    ## ---------------- REPORTING - HOW'D WE DO? -----------------------------
    ## ---------------- VISUALIZE ANNEALING ----------------------------------






    ## ---------------- DEPENDENCIES -----------------------------------------
    # Before using, you need to pip install all of these.
    import xlsxwriter
    import sys
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    ## ---------------- OPTIONS AND PARAMETERS -------------------------------

    ntmax = int(2e4)  # total number of annealing timesteps to run. 4e4 takes about 2min CPU time.

    # relative importances of the targets
    alpha = {
        'Timezone': 2**5,
        'Gender': 2**5,
        'Fullness': 2**2,
        'Requests': 2**4,
        'AsteriskFullness': 0,
        'AsteriskRequests':2**7
    }

    # Temperature function aka Annealing function.
    annealingPrefactor = sum(alpha.values())
    def kBT(ntAnneal):
        return annealingPrefactor * np.power(1 - ntAnneal / float(ntmax+2), 6)

    ## ---------------- READ INPUT FILES -------------------------------------
    ### --------------- Read faculty attributes
    ### --------------- Get student requests
    ### --------------- Read student attributes
    ### --------------- Special accommodations setup

    ## ---------------- METROPOLIS GO! ---------------------------------------
    x = -1 * np.ones((numTimeslots, numCore + numNoncore))  # faculty schedule
    y = -1 * np.ones((numTimeslots, numStudents))  # student schedule

    xPropose = np.copy(x)
    yPropose = np.copy(y)
    xMin = np.copy(x)
    yMin = np.copy(y)

    E = np.Inf
    EMin = np.Inf

    #for nt in range(ntmax):


    ### --------------- create proposal
    ### --------------- single element change of core faculty schedule
    ### --------------- pick a random slot in x (faculty schedule) and put a random student in it
    ### --------------- Special accommodations: students with partial schedules

    ### --------------- attempt single element change of non-core faculty schedule
    ### --------------- pick a random slot in x and put a student(who requested this faculty) in it

    ### --------------- eliminate student double bookings ("clones") and generate student schedules
    ### --------------- hard constraints
    ### --------------- Impose other special accomodations
    ### --------------- Compute targets
    ### --------------- Boltzmann test
    ### --------------- Min test

    ## ---------------- EXPORT TO SPREADSHEETS -----------------------------

    ## ---------------- REPORTING - HOW'D WE DO? -----------------------------
    ## ---------------- VISUALIZE ANNEALING ----------------------------------



if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = 'SampleData_RealAnon2020' # EDIT FOLDERNAME HERE
    makeSchedule(FOLDERNAME)
