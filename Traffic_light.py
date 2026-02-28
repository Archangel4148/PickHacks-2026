#Variables-------------------------------------------
MINIMUM_GAP = 3
MINIMUM_GREEN = 4
Max_green = 60
Conflicting_Phase = True # This would be configured to define if the conflicting phase occurs (a car in making a conflicting movement is present) and where the conflicting phase occurs. For now its just checking if it is true.
STOPLINE_DETECT = False

cycle_length_s = 120 # in seconds. 
Facility_Type = "Minor Arterial"
# Facility types include: Major Arterial (>40), Major Arterial (<40), Minor Arterial, Collector.
QUEUE_LENGTH = 149

PEDESTRIAN_CALL = True

PEDESTRIAN_SIGNAL_SEPARATE = False



PHASE = "Through"
Vol_per_lane = 200 # in units of veh/hr/ln. 
# Through or Left-Turn

# Functions---------------------------------------------------------

def Max_green_time(Conflicting_Phase,Facility_Type):
    if Conflicting_Phase == True:
        if Facility_Type == "Major Arterial (>40)":
            return 60 # These values could be changed to a variable that an AI edits within the ranges given in table 5-5.
        elif Facility_Type == "Major Arterial (<40)":
            return 50
        elif Facility_Type == "Minor Arterial":
            return 40
        elif Facility_Type == "Collector":
            return 30
    else:
        return 20 # Value if phase is left turn. Ranges from 15 - 30
        # Max_green_time is based on both 

def vol_cyc_max_green(Vol_per_lane: int, cycle_length_s: int) -> int:
    """
    Return Maximum Green (Gmax, s) from the table for the exact combination
    of Phase Volume per Lane (veh/hr/ln) and Cycle Length (s).

    Raises:
        KeyError if either dimension is not in the table.
    """

    # Column order: 50, 60, 70, 80, 90, 100, 110, 120 (seconds)
    cycle_lengths = [50, 60, 70, 80, 90, 100, 110, 120]

    # Table values copied from the provided image
    table = {
        100: [15, 15, 15, 15, 15, 15, 15, 15],
        200: [15, 15, 15, 15, 16, 18, 19, 21],
        300: [15, 16, 19, 21, 24, 26, 29, 31],
        400: [18, 21, 24, 28, 31, 34, 38, 41],
        500: [22, 26, 30, 34, 39, 43, 47, 51],
        600: [26, 31, 36, 41, 46, 51, 56, 61],
        700: [30, 36, 42, 48, 54, 59, 65, 71],
        800: [34, 41, 48, 54, 61, 68, 74, 81],
    }

    if Vol_per_lane not in table:
        raise KeyError(f"Phase Volume {Vol_per_lane} not in table {sorted(table.keys())}")
    if cycle_length_s not in cycle_lengths:
        raise KeyError(f"Cycle Length {cycle_length_s} not in table {cycle_lengths}")

    col = cycle_lengths.index(cycle_length_s)
    return table[Vol_per_lane][col]
# based on an 85th to 95th percentile probability of queue clearance (6). The procedure requires knowledge of the cycle length, or an estimate of its average value for actuated operation.

def DRIVER_XPCT(Facility_Type):
    if PHASE == "Through":
        if Facility_Type == "Major Arterial (>40)":
            return 10 # These values could be changed to a variable that an AI edits within the ranges given in table 5-3.
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
        return 5 # These values could be changed to a variable that an AI edits within the ranges given in table 5-4.
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
    
#Logic---------------------------------------------------------    

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
print("Maximum Green Time: ", vol_cyc_max_green(Vol_per_lane, cycle_length_s))

        
        

