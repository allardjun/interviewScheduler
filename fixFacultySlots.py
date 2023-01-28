# Part of interviewSchedule.py, for scheduling interviews between prospective grad students and PIs
# MCSB UCI Jun Allard mcsb.uci.edu, created 2020
# 
# Takes survey output from the faculty survey (not sure where it came from) in FacultyAvailabilitySurvey xlsx spreadsheet 
# returns a facultyRequestMatrix xlsx spreadsheet suitable for input into makeSchedule.py
# SLOTS must be hand-coded because of the clunky way they were returned by the survey app.

def fixFacultySlots(directoryName):

    import pandas as pd
    import numpy as np

    input_file_name = 'forBot_FacultyAvailability_wrongSlots.xlsx'
    x1 = pd.read_excel(directoryName + '/' + input_file_name)

    conversions_file_name = 'forBot_slotConversion.xlsx'
    converstion_df = pd.read_excel(directoryName + '/' + conversions_file_name, index_col=0)

    list_of_true_slots = list(converstion_df.index)
    list_of_wrong_slots = list(converstion_df.columns)
    #conversion_matrix

    #print(list_of_true_slots)
    #print(list_of_wrong_slots)


    available_slots_wrong = x1[['I am available to interview students during the following time slots:']]
    #print(available_slots_wrong)

    available_true_slots = available_slots_wrong.copy(deep=True)

    #type(available_true_slots)

    #string_of_wrong_slots = '2/6 1 - 2 PM;2/6 2 - 3 PM;2/6 3 - 4 PM;2/6 4 - 5 PM;2/7 1 - 2 PM;2/7 2 - 3 PM;2/7 3 - 4 PM;2/7 4 - 5 PM;'
    #list_of_wrong_slots = string_of_wrong_slots.split(';')


    for iFaculty,this_facultys_available_wrong_slots in available_slots_wrong.iterrows():
        print(this_facultys_available_wrong_slots.values)
        available_true_slots.iloc[iFaculty] = ''
        for i_true_slot, true_slot in enumerate(list_of_true_slots):
            can_they_make_it = 1
            for i_wrong_slot, wrong_slot in enumerate(list_of_wrong_slots):
                #print(this_facultys_available_wrong_slots.values)
                if converstion_df.iat[i_true_slot,i_wrong_slot]==1 and this_facultys_available_wrong_slots.values[0].find(wrong_slot)==-1:
                    can_they_make_it = 0
                    break
            if can_they_make_it==1:
                available_true_slots.iloc[iFaculty] = available_true_slots.iloc[iFaculty] + true_slot + '; '


    available_true_slots.to_excel(directoryName + '/forBot_FacultyAvailability_correctedSlots.xlsx')




if __name__ == '__main__':
    # write the folder containing input data. Output data will be written to same folder.
    FOLDERNAME = '~/Dropbox/science/service/MCSB/Admissions/2023Entry/03RecruitmentVisit/PreliminaryData' # EDIT FOLDERNAME HERE
    #FOLDERNAME = 'SampleData_RealAnon'
    fixFacultySlots(FOLDERNAME)    