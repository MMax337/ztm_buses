# BusStatistician Profiling Results

## Overall Creation
- **With Profiling:** 31.705 seconds
- **Without Profiling:** 16.033 seconds

### Most Time-Consuming Operations:

1. **Time Changer Function:**
   - Cumulative Time (cumtime): 25.777 s
   - Total Time (tottime): 0.715 s
   - Number of calls: 1,519,689
   - Calls to `datetime.datetime.strptime` (cumtime): 25.036 s
   - 81.3% of the time spent on converting str to `datetime.datetime`

2. **JSON Decoding:**
   - Total Time: 1.418 s

3. **Setting Buses:**
   - Total Time: 0.985 s

4. **Adding the State to Each Bus:**
   - Total Time: 0.679 s

## BusStatistician.get_speed_statistics
- **With Profiling:** 2.677 s
- **Without Profiling:** 1.484 s

### Time Distribution in Bus.speed_compute:
- Total Time (tottime): 1.06 s
- Cumulative Time (cumtime): 2.19 s

   - This method called `Coordinates.distance`:
      - Total Time: 0.543 s

## BusStatistician.get_punctuality_statistics
- **With Profiling:** 37.892 s
- **Without Profiling:** 16.003 s

### Main Contributors to Total Time:

1. **Time Difference in Bus.determine_route (Computing Time Difference in Seconds):**
   - Total Time: 13.823 s
   - Cumulative Time: 22.129 s
   - Function called 62,642 times

2. **Bus.determine_route:**
   - Total Time: 2.698 s
   - Cumulative Time: 33.361 s

3. **Bus.punctuality_compute:**
   - Total Time: 1.095 s
   - Cumulative Time: 37.48 s
