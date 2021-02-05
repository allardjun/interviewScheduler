def scratch2ObjectTest():
    print("Hello world!")

    currentTargets = Targets()

    print(currentTargets.fractionGenderedMeeting)

    print(currentTargets.FractionFull["min"])

    print([a for a in dir(currentTargets) if not a.startswith('__')])

    newTargets = currentTargets.copy()

    print(newTargets.FractionFull["min"])
    newTargets.FractionFull["min"] = 7
    print(newTargets.FractionFull["min"])
    print(currentTargets.FractionFull["min"])

    print(vars(currentTargets))

    for iTargetName, iTargetValue in vars(currentTargets).items():
        if isinstance(iTargetValue,dict):
            print(iTargetName)
            print(iTargetValue['min'])
            print(iTargetValue['total'])
        else:
            print(iTargetName)
            print(iTargetValue)
        #print(currentTargets.iTarget)

    for i, iTarget in enumerate(vars(currentTargets).items()):
        print(getattr(currentTargets,iTarget[0]))

    for i, iTarget in enumerate(vars(proposalTargets).items(),start=1):
        if isinstance(iTarget[1],dict): # if it's a target with a min and a mean
            ax = fig.add_subplot(numberOfPlots, 1, i)
            ax.title.set_text(iTarget[0])
            for nt in ntToPlot[::100]:
                plt.plot(nt,getattr(listOfTargets[nt],iTarget[0])['min'], '+b')
                plt.plot(nt,getattr(listOfTargets[nt],iTarget[0])['mean'], 'or')
        else:
            ax = fig.add_subplot(numberOfPlots, 1, i)
            ax.title.set_text(iTarget[0])
            for nt in ntToPlot[::100]:
                plt.plot(nt,getattr(listOfTargets[nt],iTarget[0]), '+k')

    print(len(vars(currentTargets)))

class Targets:
    def __init__(self):
        self.E = 0
        self.numberTimezoneViolations = 0
        self.fractionGenderedMeeting = 0
        self.facultyMeetingTooManyStudents = 0
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


        targetCopy.E = self.E
        targetCopy.numberTimezoneViolations    = self.numberTimezoneViolations
        targetCopy.fractionGenderedMeeting = self.fractionGenderedMeeting
        targetCopy.facultyMeetingTooManyStudents = self.facultyMeetingTooManyStudents
        targetCopy.numStudentsCriticallyLow = self.numStudentsCriticallyLow
        targetCopy.FractionAsteriskFull['min'] = self.FractionAsteriskFull['min']
        targetCopy.FractionAsteriskFull['total'] = self.FractionAsteriskFull['total']
        targetCopy.FractionFull['min'] = self.FractionFull['min']
        targetCopy.FractionFull['total'] = self.FractionFull['total']
        return targetCopy

if __name__ == '__main__':
    scratch2ObjectTest()
