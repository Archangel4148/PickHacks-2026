MINIMUM_GAP = 3
MINIMUM_GREEN = 4

Facility_Type = "Minor Arterial" 
# Facility types include: Major Arterial (>40), Major Arterial (<40), Minor Arterial, Collector.
QUEUE_LENGTH = 149

PEDESTRIAN_CALL = True

PEDESTRIAN_SIGNAL_SEPARATE = False

STOPLINE_DETECT = False

PHASE = "Through"
# Through or Left-Turn

def DRIVER_XPCT(Facility_Type):
    if PHASE == "Through":
        if Facility_Type == "Major Arterial (>40)":
            return 10 #These values could be changed to a variable that an AI edits. Currently they are set to the lowest value in the table.
        elif Facility_Type == "Major Arterial (<40)":
            return 7
        elif Facility_Type == "Minor Arterial":
            return 4
        elif Facility_Type == "Collector":
            return 2
    else:
        return 2
    
def PEDESTRIAN_TIME():
    return 9 # This value should be based on walk interval duration + pedestrian clearance interval duration. It is currently set to a value that would satisfy the pedestrian signal requirements for a  18 ft crosswalk with a 3 ft/s walking speed and a 3 second clearance interval.

def QUEUE_CLEARANCE(QUEUE_LENGTH):
    if QUEUE_LENGTH >= 0 and QUEUE_LENGTH <= 25:
        return 5
    elif QUEUE_LENGTH > 25 and QUEUE_LENGTH <= 50:
        return 7
    elif QUEUE_LENGTH > 50 and QUEUE_LENGTH <= 75:
        return 9
    elif QUEUE_LENGTH > 75 and QUEUE_LENGTH <= 100:
        return 11
    elif QUEUE_LENGTH > 100 and QUEUE_LENGTH <= 125:
        return 13
    elif QUEUE_LENGTH > 125 and QUEUE_LENGTH <= 150:
        return 15
    

#if STOPLINE_DETECT == False:
   # VAR_INITIAL() # A system to allow vehicles queued between the stop line and the nearest detector at the start of green to clear the inersection.


if PHASE == "Through":
    if STOPLINE_DETECT == True:
        if PEDESTRIAN_CALL == True:
            MINIMUM_GREEN = DRIVER_XPCT(Facility_Type) # Calls the table which gives the mimum green time needed to satisfy driver expectancy based on facility type.
        else:
            MINIMUM_GREEN =  max(DRIVER_XPCT(Facility_Type), PEDESTRIAN_TIME()) # Finds the maximum time from the two functions to use for MINIMUM_GREEN
    else: 
        if PEDESTRIAN_CALL == True:
            MINIMUM_GREEN = max(DRIVER_XPCT(Facility_Type), QUEUE_CLEARANCE(QUEUE_LENGTH)) # Finds the maximum time from the two functions to use for MINIMUM_GREEN
        else:
            MINIMUM_GREEN = max(DRIVER_XPCT(Facility_Type), PEDESTRIAN_TIME(), QUEUE_CLEARANCE(QUEUE_LENGTH)) # Finds the maximum time from the three functions to use for MINIMUM_GREEN
elif PHASE == "Left-Turn":
    if STOPLINE_DETECT == True:
            MINIMUM_GREEN = DRIVER_XPCT(Facility_Type) # Calls the table which gives the minimumgreen time needed to satisfy driver expectancy based on facility type.

print("Minimum Green Time: ", MINIMUM_GREEN)


        
        

