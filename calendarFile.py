#week long calendar


class Event:
    def __init__(self, name, startTime, endTime, announced = False):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.announced = announced

    def getName(self):
        return self.name
    
    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime
    
    def changeStartTime(self, newStartTime):
        self.startTime = newStartTime

    def changeEndTime(self, newEndTime):
        self.endTime = newEndTime
    

         
class Day:
    def __init__(self, dayOfWeek):
        self.dayOfWeek = dayOfWeek
        self.events = []

    def addEvent(self, newEvent):#either returns 0 meaning it happened successfully, or returns an event, which is the event which overlaps
        eventTimings = []
        for event in self.events:
            eventTimings.append([event.getStartTime(), event.getEndTime()])
        #checking if an event is already there 
        for i, eventTiming in enumerate(eventTimings):
            # if (newEvent.getStartTime() > eventTiming[0] and newEvent.getStartTime() < eventTiming[1]) or (newEvent.getEndTime() > eventTiming[0] and newEvent.getEndTime() < eventTiming[1]):
            if newEvent.getStartTime() == eventTiming[0]:
                return self.events[i]

        for i in range(len(self.events)):
            if newEvent.getEndTime() <= self.events[i].getStartTime():
                self.events.insert(i, newEvent)
                self.printEvents()
                return 0
            
        self.events.append(newEvent)
        self.printEvents()
        return 0

    def removeEventName(self, name):#removes event. returns 0 if successful, -1 if not successful
        for i, event in enumerate(self.events):
            if event.getName() == name:
                self.events.pop(i)
                return 0
        return -1

    def removeEventStartTime(self, startTime):#removes an event based on its start time
        for i, event in enumerate(self.events):
            if event.getStartTime() == startTime:
                self.events.pop(i)
                return 0
        return -1

    def removeAllEvents(self):
        self.events = []
    
    def printEvents(self): #FOR TESTING
        print("printing events in day")
        eventsPrint = []
        for event in self.events:
            eventsPrint.append([event.name, event.startTime])
        print(eventsPrint)
    
    def checkEvent(self, time):
        print("events in day in calendar: ")
        self.printEvents()
        for event in self.events:
            if int(event.getStartTime()) == int(time):
                return event.getName()
        return 0
    
class CalendarClass:

    def __init__(self, currentDayIndex = 0): #default starts as monday
        self.days = [Day("Monday"),Day("Tuesday"),Day("Wednesday"),Day("Thursday"),Day("Friday"),Day("Saturday"),Day("Sunday")]
        self.currentDayIndex = currentDayIndex
        self.dayIndexer = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        self.readFromFile()
    def changeDay(self):
        self.days[self.currentDayIndex].removeAllEvents()
        self.currentDayIndex = (self.currentDayIndex + 1) % 7

    def possibleChangeDay(self, newDayIndex):
        # if newDayIndex != self.currentDayIndex:
        #     self.days[self.currentDayIndex].events = []
        #     self.currentDayIndex = newDayIndex
        pass

   

    def check(self, day, time):
        if day == "today":
            dayIndex = self.currentDayIndex
        elif day == "tomorrow":
            dayIndex = (self.currentDayIndex + 1) % 7
        elif day == "yesterday":
            dayIndex = (self.currentDayIndex - 1) % 7
        else:
            dayIndex = self.dayIndexer[day]
        
        #10 a.m or 2 p.m
        time = self.convertTime(time)
        day = self.days[dayIndex]
        return day.checkEvent(time)
    
    def plan(self, day, time, activity):
        if day == "today":
            dayIndex = self.currentDayIndex
        elif day == "tomorrow":
            dayIndex = (self.currentDayIndex + 1) % 7
        elif day == "yesterday":
            dayIndex = (self.currentDayIndex - 1) % 7
        else:
            dayIndex = self.dayIndexer[day]
        
        #10 a.m or 2 p.m
        time = self.convertTime(time)
        day = self.days[dayIndex]
        event = Event(activity, time, time)
        response = day.addEvent(event)
        self.writeToFile()
        return response

    def setAlarm(self, day, time):
        return self.plan(day, time, "alarm")

    def convertTime(self, time):
        print("trying to convert this time")
        print(time)
        AmOrPm = time[len(time)-3:]
        number = int(time[:len(time)-4])
        print("AmOrPm: ", AmOrPm)
        print("number: ", number)

        if AmOrPm =="p.m":
            number += 12
        number *= 100
        print("time number is: ", number)
        print("returning the number: ", self.convertDateStringToInt(str(number)))
        return self.convertDateStringToInt(str(number))
    
    def convertDateStringToInt(self, stringTime): #"0145" -> 105
        while len(stringTime) < 4:
            stringTime = "0"+stringTime
        hours = int(stringTime[0:2])
        minutes = int(stringTime[2:])
        return hours*60 + minutes

    def convertDateIntToString(self, intTime): #105 -> "1045"
        hours = 0
        minutes = 0
        while intTime >= 60:
            hours+=1
            intTime -= 60

        if hours < 10:
            hours = "0" + str(hours)
        else:
            hours = str(hours)
        
        if intTime < 10:
            minutes = "0" + str(intTime)
        else:
            minutes = str(intTime)
        return hours + minutes
    
    def checkAnnouncements(self, stringTime): #time is given as "1450" for example
        stringTime = int(self.convertDateStringToInt(stringTime))
        day = self.days[self.currentDayIndex]
        for event in day.events:
            if event.name == "alarm" and (not event.announced) and stringTime >= event.startTime:
                event.announced = True
                return "alarm" 
            elif event.name[:8] == "reminder" and (not event.announced) and stringTime >= event.startTime:
                event.announced = True
                return event.name
            elif (not event.announced) and stringTime >= event.startTime - 15:
                event.announced = True
                return event.name 
        return None

    def writeToFile(self):
        with open('calendar.txt', 'w') as f:
            for i in range(7):
                day = self.days[i]
                for event in day.events:
                    f.write(day.dayOfWeek + " " + event.name + " " + str(event.startTime) + " " + str(event.announced))
                    f.write("\n")

    def readFromFile(self):
        try:
            f = open("calendar.txt", "r")
        except:
            print("no file to read calendar from")
            return
        for line in f:
            if len(line) < 3:
                continue
            arr = line.split(" ")
            arr[-1] = arr[-1][:len(arr[-1])-1]
            print(arr)
            dayOfWeek = arr[0].lower()
            announced = arr[-1]
            time = arr[-2]
            eventName = " ".join(arr[1:len(arr)-2])
            day = self.days[self.dayIndexer[dayOfWeek]]
            newEvent = Event(eventName, int(time), int(time), announced)
            day.addEvent(newEvent)
            

        f.close()
    
    def clearCalendar(self):
        for day in self.days:
            day.removeAllEvents()
    

def test():
    calendar = CalendarClass()
    calendar.readFromFile()
    calendar.days[0].printEvents()
    print("checking now")
    print(calendar.check("monday", "2 p.m"))
    print("end")
