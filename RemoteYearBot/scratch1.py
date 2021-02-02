a = 1
b = 2

print(a+b)

b = 1

print(a+b)

for ilist in range(len(facultyNamesFromStudents)):
if not (facultyNamesFromStudents[ilist] == facultyNames[ilist]):
    print('The faculty names in the xlsx files do not match.')
    print(facultyNamesFromStudents[ilist])
    print(facultyNames[ilist])
