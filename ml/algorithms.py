import numpy
import csv
from stat_funcs import *
from jsonTOcsv import *
from parsers import *
from pprint import pprint

#Used the saved csv and JSON files to calculate mold risk based on simple
#isopleth model, and experiment with detecting moved nodes as well as 
#appliance failure.

#time, days, fraction required for condition
TIME_REQ = 480
DAY_REQ = 14
FRAC_REQ = .3

#risk scalars
HI = 1.1
MED = .8
LOW = .6

stdsNeeded = 2
stdsWanted = .2

def weatherChange():
    return True

#isopleth formula
def func(temp):
    return 104 * math.e ** (-.05786 * temp)

def isopleth_risk(temp, hum):
    if hum >=  HI * func(temp):
        return 'high'
    if hum >= MED * func(temp):
        return 'med'
    if hum >= LOW * func(temp):
        return 'low'
    return 'none'

def isopleth(temp, hum):
    if hum >= func(temp):
        return True
    return False

#returns time difference in minutes, rounds up to at least one minute if zero
def time_dif(old, new):
    time = 0.0
    time += 30 * 24 * 60 * (int(new[5:7]) - int(old[5:7])) #months
    time += 24 * 60 * (int(new[8:10]) - int(old[8:10])) #days
    time += 60 * (int(new[11:13]) - int(old[11:13])) #hours
    time += int(new[14:16]) - int(old[14:16]) #minutes
    if time == 0:
        return 1
    return time

#returns true if same day, false otherwise
def same_day(one, two):
    if one[:10] == two[:10]:
        return True
    return False

def str_dif(old, new):
    return int(new) - int(old)

def float_dif(old, new):
    return float(new) - float(old)

#minimum conditions for mold
def cond(time_avg, time_frac):
    if time_avg > TIME_REQ and time_frac > FRAC_REQ:
        return True
    return False

def average_time(groups):
    times = []
    for group in groups:
        for i in range(1, len(group)):
            times.append(time_dif(group[i - 1]['time'], group[i]['time']))
    return times

#uses isopleth function to determine if a point is above the isopleth, and then
#uses cond to determine if that sensor is in moldy conditions
def mold(groups):
    positives = []
    risks = []
    x = []
    y = []
    cond_counter = 0
    for group in groups:
        flag = False
        up_counter = 0
        simple_counter = 0
        strat_counter = [0, 0, 0, 0]
        all_times = []
        for object in group:
            if flag:
                if isopleth(object['TEMP'], object['RH']):
                    up_counter += time_dif(last_time, object['time'])
                    simple_counter += 1
                    positives.append(object)
                    strat_counter[0] += 1
                else:
                    all_times.append(up_counter)
                    up_counter = 0
                    flag = False
            else:
                if isopleth(object['TEMP'], object['RH']):
                    flag = True
                    last_time = object['time']
                    simple_counter += 1
                    positives.append(object)
                else:
                    pass
            if isopleth_risk(object['TEMP'], object['RH']) == 'med':
                strat_counter[1] += 1
            elif isopleth_risk(object['TEMP'], object['RH']) == 'low':
                strat_counter[2] += 1
            elif isopleth_risk(object['TEMP'], object['RH']) == 'none':
                strat_counter[3] += 1
            else:
                pass
        if cond(avg(all_times), float(simple_counter) / float(len(group))):
            cond_counter += 1
        if strat_counter[0] == max(strat_counter):
            risks.append('high')
        elif strat_counter[1] == max(strat_counter):
            risks.append('med')
        elif strat_counter[2] == max(strat_counter):
            risks.append('low')
        elif strat_counter[3] == max(strat_counter):
            risks.append('none')
        else:
            pass
    print(cond_counter, len(groups), float(cond_counter) / float(len(groups)))
    if len(positives) > 0:
        for object in positives:
            x.append(object['TEMP'])
            y.append(object['RH'])
        coef4 = numpy.polyfit(numpy.array(x), numpy.array(y), 4)
        coef3 = numpy.polyfit(numpy.array(x), numpy.array(y), 3)
        coef2 = numpy.polyfit(numpy.array(x), numpy.array(y), 2)
        print(2, coef2)
        print(3, coef3)
        print(4, coef4)
        print("risks", risks)

def mold_daily():
    all_days = days()
    all_grouper = {}
    streaks = []
    for day in all_days:
        groups, grouper = day_parse(day)
        for group in groups:
            flag = False
            up_counter = 0
            all_times = []            
            for object in group:
                if flag:
                    if isopleth(object['TEMP'], object['RH']):
                        up_counter += time_dif(last_time, object['time'])
                    else:
                        all_times.append(up_counter)
                        up_counter = 0
                        flag = False
                else:
                    if isopleth(object['TEMP'], object['RH']):
                        flag = True
                        last_time = object['time']
                    else:
                        pass
            if len(all_times) > 0:
                max_time = max(all_times)
            else:
                max_time = 0
            if object['snid'] in all_grouper:
                streaks[all_grouper[object['snid']]].append(max_time)
            else:
                all_grouper[object['snid']] = len(streaks)
                streaks.append([max_time])          
            #ENDFOR
        #ENDFOR    
    #ENDFOR
    positives = []
    for lst in streaks:
        flag = False
        current = 0
        for val in lst:
            if val > TIME_REQ:
                current += 1
            else:
                if current > DAY_REQ:
                    flag = True
                else:
                    pass
                current = 0
        if flag:
            positives.append(1)
        else:
            positives.append(0)
        #ENDFOR
    #ENDFOR
    instances = sum(positives)
    total = len(positives)
    print(instances, total, float(instances) / float(total))

#smart temp
#if temp moves faster than some number of standard deviations (in the absense of
#node moved) then alert for drastic change. can also be applied to the other
#measurements. have to figure out what drastic means (in terms of standard
#deviations) by opening garage door, putting sensor in fridge, putting sensor
#outside, etc
def smart_temp(groups):
    temp_stddev = []
    temp_mean = []
    for group in groups:
        temp_delta = []
        flag = False
        for object in group:
            if flag:
                deltat = time_dif(prev['time'], object['time'])
                if deltat > 0:
                    temp_delta.append(float(object['TEMP'] - prev['TEMP']) / deltat)
            else:
                flag = True
            prev = object
        temp_stddev.append(std(temp_delta))
        temp_mean.append(avg(temp_delta))
    
    for i in range(len(temp_stddev)):
        if temp_stddev[i] < .02:
            temp_stddev[i] = .02
    return [temp_stddev, temp_mean]

#node moved
#if node moved packet is received, wait till node moved packets stop (they do
#not happen for at least 2 minutes) and then compare standard deviations of all
#measurements before and after. if sum of all is above some number, then alert
#NOTE: can generally be used for any situation in which sudden changes need to
#be monitored. only change is that this is only looked at when moved packets are
#being sent, and in other situations changes would always have to be monitored
def node_moved(groups):
    for type in ['TEMP', 'RH', 'COND', 'snr']:
        type_stddev = []
        type_mean = []
        for group in groups:
            delta = []
            flag = False
            for object in group:
                if flag:
                    deltat = time_dif(prev['time'], object['time'])
                    if deltat > 0:
                        delta.append(float(object[type] - prev[type]) / deltat)
                else:
                    flag = True
                prev = object
            type_stddev.append(std(delta))
            type_mean.append(avg(delta))
        #very small std devs can cause errors because small deviations will be
        #very large std devs, so make all min .02
        stddev_avg = avg(type_stddev)
        for i in range(len(type_stddev)):
            if type_stddev[i] < .3 * stddev_avg:
                type_stddev[i] = .3 * stddev_avg    
        if type == 'TEMP':
            temp_sd = type_stddev
            temp_m = type_mean
        elif type == 'RH':
            rh_sd = type_stddev
            rh_m = type_mean
        elif type == 'COND':
            cond_sd = type_stddev
            cond_m = type_mean
        elif type == 'snr':
            snr_sd = type_stddev
            snr_m = type_mean
    return [[temp_sd, temp_m], [rh_sd, rh_m], [cond_sd, cond_m], [snr_sd, snr_m]]

#HVAC performance without sensor on top of vent
#when temp changes:
#-calculate the minimum temp it reaches before returning to regular temp
#-calculate rate of recovery
#-have to determine how to know if this rate of recovery is suboptimal - must be
# sensor specific, but it is not known whether or not the average that the
# sensor encounters is optimal or not
def performance(snid, groups, grouper):
    #go through temp data
    #if temp ever deviates by more than x std devs:
    #-check if outdoor temp changed then (and if HVAC turned off if
    # there are sensor in place to do that)
    #-if so, calculate time till temp returns to original temp
    #-figure out some way to evaluate the performance of the sensor -
    # must be based on time it takes to recover as well as the outdoor
    # temp, and how far indoor temp went
    
    #the only thing that can be changed is instead of using the average of all
    #the temps, use the temp that the user has set for their thermostat because
    #that might not be the average
    temps = []
    times = []
    recovers = []
    peaks = []
    for object in groups[grouper[snid]]:
        temps.append(object['TEMP'])
        times.append(object['time'])
    average = avg(temps)
    stddev = std(temps)
    for i in range(len(temps)):
        if abs(temps[i] - average) / stddev > stdsNeeded:
            if weatherChange():
                start = -1
                end = -1
                for j in range(i, 0, -1):
                    if abs(temps[j] - average) / stddev < stdsWanted:
                        start = j
                        break
                k = i
                while(k < len(temps)):
                    if abs(temps[k] - average) / stddev < stdsWanted:
                        end = k
                        break
                    else:
                        k += 1
                if start > -1 and end > -1:
                    recovers.append(time_dif(times[start], times[end]))
                    if (temps[i] - average) / stddev < 0:
                        peaks.append(average - min(temps[j:k]))
                    else:
                        peaks.append(max(temps[j:k]) - average)
                else:
                    pass
            else:
                pass
    if len(recovers) != 0:
        performance = avg(recovers) / avg(peaks)
    else:
        performance = 0
    return performance

def all_perform(groups):
    all_performance = []
    for group in groups:
        temps = []
        times = []
        recovers = []
        peaks = []    
        for object in group:
            temps.append(object['TEMP'])
            times.append(object['time'])
        stddev = std(temps)
        average = avg(temps)
        if stddev == 0:
            all_performance.append(0)
            continue
        for i in range(len(temps)):
            if abs(temps[i] - average) / stddev > stdsNeeded:
                if weatherChange():
                    start = -1
                    end = -1
                    for j in range(i, 0, -1):
                        if abs(temps[j] - average) / stddev < stdsWanted:
                            start = j
                            break
                    k = i
                    while(k < len(temps)):
                        if abs(temps[k] - average) / stddev < stdsWanted:
                            end = k
                            break
                        else:
                            k += 1
                    if start > -1 and end > -1:
                        recovers.append(time_dif(times[start], times[end]))
                        if (temps[i] - average) / stddev < 0:
                            peaks.append(average - min(temps[j:k]))
                        else:
                            peaks.append(max(temps[j:k]) - average)
                    else:
                        pass
                else:
                    pass
        if len(recovers) != 0 and avg(peaks) != 0:
            performance = avg(recovers) / avg(peaks)
        else:
            performance = 0
        all_performance.append(performance)
    return all_performance
#HVAC performance with sensor on top of vent
#-when HVAC is on (not known how we will determine this)
#-use API of some weather site to find temp based on location
#-if difference between outdoor temp and air temp is less than 20, alert

#need to find and analyze all the completely stationary sensors
def find_stationary():
    snid_list = ['90-7a-f1-ff-fc-7c']
    data = []
    for snid in snid_list:
        new_data = snid_parse(snid)
        data.append(new_data)
    #ENDFOR
    for snid in data:
        snrs = []      
        for object in snid:
            new_snrs = []
            new_snrs.append(object['snr'])
        #ENDFOR
        snrs.append(new_snrs)
    #ENDFOR
    delta = []
    for snid in snrs:
        new_delta = []
        for j in range(1, len(snid)):
            new_delta.append(snid[i] - snid[i - 1])
        #ENDFOR
        delta.append(new_delta)
    #ENDFOR
    forstd = flatten(delta)
    print(std(forstd))
    return (data, snrs, delta)

def find_vent():
    snid = '90-7a-f1-ff-fc-ae'
    data = snid_parse(snid)
    temps = []
    off = []
    on = []
    delta_temp = []
    for object in data:
        new_temp = object['TEMP']
        temps.append(new_temp)
        if new_temp < 30:
            off.append(object['RH'])
        else:
            on.append(object['RH'])
    for i in range(1, len(temps)):
        delta_temp.append(temps[i] - temps[i - 1])
    print(std(delta_temp))
    print(avg(on), avg(off))
    return (temps, delta_temp)

def all_normalized_data():
    all_snids = flatten(snid_reader())
    #all_snids = ['90-7a-f1-ff-fc-ae']
    for snid in all_snids:
        data = []
        deltas = [[], [], [], []]
        dts = []
        try:
            with open('/Users/ritvik/Desktop/csv/' + snid + '.csv', 'rb') as csvfile:
                datareader = csv.reader(csvfile, delimiter=',', \
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in datareader:
                    data.append(row)
            #ENDWITH
        except IOError:
            continue
        #ENDTRY
        for i in range(1, len(data)):
            dt = time_dif(data[i - 1][1], data[i][1])
            dts.append(dt)
            deltas[0].append(float_dif(data[i - 1][2], data[i][2]) / dt) #snr
            deltas[1].append(str_dif(data[i - 1][3], data[i][3]) / dt) #temp
            deltas[2].append(str_dif(data[i - 1][4], data[i][4]) / dt) #rh
            deltas[3].append(str_dif(data[i - 1][5], data[i][5]) / dt) #cond
        #ENDFOR
        for i in range(0, 4):
            #deltas[i] = normalize(deltas[i])
            deltas[i] = normalizeInSections(deltas[i], dts, 14)
        #ENDFOR
        with open('/Users/ritvik/Desktop/analysis/' + snid + '.csv', 'wb') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',', \
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvfile.seek(0, 2)
            for i in range(len(deltas[0])):
                datawriter.writerow([deltas[0][i]] + [deltas[1][i]] + \
                                    [deltas[2][i]] + [deltas[3][i]])
            csvfile.seek(0, 0)
            #can now analyze data, which is data for just current snid, and
            #then put in csv file to be learned in matlab
        #ENDWITH
        with open('/Users/ritvik/Desktop/all_data.csv', 'a+') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',', \
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvfile.seek(0, 2)
            for i in range(len(deltas[0])):
                datawriter.writerow([deltas[0][i]] + [deltas[1][i]] + \
                                    [deltas[2][i]] + [deltas[3][i]])
            csvfile.seek(0, 0)
        #ENDWITH
    #ENDFOR