# -*- coding: utf-8 -*-
"""Data Generator.ipynb


ADD: trucks not being used because they are not needed

Generate a list that has the number of trucks needeed per day and check if the trucks are needed per day
"""

import datetime
import numpy as np
import scipy.stats as stats
import csv
import math
import random

# Based 'currentDate', generates the next failure date and next maintenance date
def iterateDates(currentDate, maintenanceSchedule, avgMTTF, MTTFstdev):
    nextFailureDate = currentDate + datetime.timedelta(days = np.random.normal(avgMTTF, MTTFstdev))
    nextFailureDate = nextFailureDate.replace(hour = 0, minute=0, second=0, microsecond=0)
    nextMaintenanceDate = currentDate + datetime.timedelta(days = maintenanceSchedule)
    return nextFailureDate, nextMaintenanceDate

# Splits list into n smaller lists
def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

# Gets the class and model for each truck (each equipmentID) based on the total number of trucks (equipmentIDs) and the percent of trucks that are assigned to "Haul"
# As it iterates down the list of equipmentIDs, the model is assigned on a rolling basis and resets to the first model in the list when it reaches the end
def getTruckClassAndModel(numTrucks, percentHaul):
    finalList = []

    modelDict = {"Haul": ["Cat 785", "Cat 789", "Cat 793C", "Cat 793D", "Cat 793F MARC", "Cat 793F MEM"], "Shovel": ["Cat 992G", "Cat 994", "Cat 994F", "Cat 994H", "Hitachi 3600", "Hitachi 3601", "Hitachi 5500", "Hitachi 5600"]}
    classList = ["Haul", "Shovel"]
    numHaulTrucks = math.ceil(numTrucks * percentHaul)
    currentHaulModel = 0
    currentShovelModel = 0

    for i in range(numTrucks):
      if i < numHaulTrucks:
        finalList.append([classList[0], modelDict[classList[0]][currentHaulModel]])
        if currentHaulModel == 5:
          currentHaulModel = 0
        else:
          currentHaulModel += 1
      else:
        finalList.append([classList[1], modelDict[classList[1]][currentShovelModel]])
        if currentShovelModel == 7:
          currentShovelModel = 0
        else:
          currentShovelModel += 1

    return finalList

def calculateData(inUse, truckRepaired, repairReason, truckClass, truckModel):
  avgLoadTime, avgUnloadTime, avgLoadWaitTime, avgUnloadWaitTime, cycleTime, timeToRepair, repairCost, maintenanceCost, payload, payloadPrice, costofTruck = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
  payloadLimits = {"Cat 785": 138799, "Cat 789": 193230, "Cat 793C": 228611, "Cat 793D": 228611, "Cat 793F MARC": 232239, "Cat 793F MEM": 232239}
  truckPrices = {"Cat 785": 3400000, "Cat 789": 4000000, "Cat 793C": 4500000, "Cat 793D": 4500000, "Cat 793F MARC": 5000000, "Cat 793F MEM": 5000000, "Cat 992G": 200000, "Cat 994": 300000, "Cat 994F": 350000, "Cat 994H": 370000, "Hitachi 3600": 400000, "Hitachi 3601": 450000, "Hitachi 5500": 500000, "Hitachi 5600": 550000}
  materialToOreRatio = 0.2
  priceOfOrePerKG = 2

  # RepairCost, MaintenanceCost, and TimeToRepair
  if inUse == "N" and truckRepaired == "Y" and repairReason == "Broken":
    repairCost = round(random.uniform(500, 2000),2)
    timeToRepair =  round(stats.truncnorm.rvs((30 - 120) / 600, (720 - 120) / 600, loc=120, scale=600), 2)
  elif inUse == "N" and truckRepaired == "Y" and repairReason == "Maintenance":
    maintenanceCost = round(random.uniform(500, 2000),2)
    timeToRepair = round(stats.truncnorm.rvs((30 - 120) / 600, (720 - 120) / 600, loc=120, scale=600), 2)

  # AvgLoadTime, AvgUnloadTime, AvgLoadWaitTime, avgUnloadWaitTime, CycleTime
  if inUse == "Y":
    cycleTime = np.random.normal(90, 20)
    avgLoadTime = np.random.normal(15, 5)
    avgUnloadTime = np.random.normal(5, 2)
    avgLoadWaitTime = np.random.normal(25, 5)
    avgUnloadWaitTime = np.random.normal(10, 5)
    if truckClass == "Haul":
      payload = round(stats.truncnorm.rvs(((payloadLimits[truckModel]/2) - (payloadLimits[truckModel]*0.8)) / (payloadLimits[truckModel]*0.2), (payloadLimits[truckModel] - (payloadLimits[truckModel]*0.8)) / (payloadLimits[truckModel]*0.2), loc=(payloadLimits[truckModel]*0.8), scale=(payloadLimits[truckModel]*0.2)), 2)
      payloadPrice = payload * materialToOreRatio * priceOfOrePerKG

  costofTruck = truckPrices[truckModel]
  
  return avgLoadTime, avgUnloadTime, avgLoadWaitTime, avgUnloadWaitTime, cycleTime, timeToRepair, repairCost, maintenanceCost, payload, payloadPrice, costofTruck

# Generates the truck data
def generateTruckData(numTrucks, chanceInUse, avgMTTF, MTTFstdev, maintenanceSchedule, startDate, endDate):

    totalTruckList = []
    maintenanceList = [[] for _ in range((endDate-startDate).days)]
    # List of "Class" and "Model" for each equipmentID
    truckClassAndModelList = getTruckClassAndModel(numTrucks, 0.7)

    # Loops through all equpmentIDs
    for i in range(numTrucks):
      dayNum = 0
      truckList = []
      currentDate = startDate
      nextFailureDate, nextMaintenanceDate = iterateDates(currentDate, maintenanceSchedule, avgMTTF, MTTFstdev)
      # Loops through all days between startDate and endDate
      while currentDate != endDate:
        inUse = "Y"
        truckRepaired = "N"
        repairReason = "N/A"
        if currentDate == nextFailureDate:
          nextFailureDate, nextMaintenanceDate = iterateDates(currentDate, maintenanceSchedule, avgMTTF, MTTFstdev)
          inUse = "N"
          truckRepaired = "Y"
          repairReason = "Broken"
        # If the truck is maintained, the truck takes on average an extra month to fail
        elif currentDate == nextMaintenanceDate:
          nextFailureDate, nextMaintenanceDate = iterateDates(currentDate, maintenanceSchedule, avgMTTF, MTTFstdev)
          inUse = "N"
          truckRepaired = "Y"
          repairReason = "Maintenance"
        else:
          randomVar = random.uniform(0, 1)
          if randomVar >= chanceInUse:
            inUse = "N"
        avgLoadTime, avgUnloadTime, avgLoadWaitTime, avgUnloadWaitTime, cycleTime, timeToRepair, repairCost, maintenanceCost, payload, payloadPrice, costofTruck = calculateData(inUse, truckRepaired, repairReason, truckClassAndModelList[i][0], truckClassAndModelList[i][1])
        truckList.append([currentDate, i+1, truckClassAndModelList[i][0], truckClassAndModelList[i][1], inUse, truckRepaired, repairReason, avgLoadTime, avgUnloadTime, avgLoadWaitTime, avgUnloadWaitTime, cycleTime, timeToRepair, repairCost, maintenanceCost, payload, payloadPrice, costofTruck])
        if timeToRepair != "N/A":
          maintenanceList[dayNum].append(timeToRepair)
        currentDate += datetime.timedelta(days=1)
        dayNum += 1

      totalTruckList.append(truckList)

    return totalTruckList, maintenanceList

def generateMaintenanceData(numBays, startDate, endDate, maintenanceList):
    totalBayList = []

    # Loops through all bayIDs
    for i in range(numBays):
      dayNum = 0
      bayList = []
      currentDate = startDate
      # Loops through all days between startDate and endDate
      while currentDate != endDate:
        inUse = "N"
        jobsCompleted = 0
        totalTime = 0
        maintenanceJobs = list(split(maintenanceList[dayNum], numBays))[i]
        totalMaintenanceJobs = len(maintenanceJobs)
        for idx in range(totalMaintenanceJobs):
          totalTime += maintenanceJobs[idx]
          if totalTime >= 480:
            jobsCompleted = idx
            break
          jobsCompleted = totalMaintenanceJobs
        if len(maintenanceJobs) >= 1:
          inUse = "Y"
        bayList.append([currentDate, i+1, inUse, totalMaintenanceJobs, jobsCompleted, totalMaintenanceJobs-jobsCompleted])
        currentDate += datetime.timedelta(days=1)
        dayNum += 1

      totalBayList.append(bayList)

    return totalBayList

startDate = datetime.datetime(2018, 1, 1)
endDate = datetime.datetime(2022, 12, 31)

totalTruckList, maintenanceList = generateTruckData(numTrucks=50, chanceInUse=0.95, avgMTTF=60, MTTFstdev=15, maintenanceSchedule=60, startDate=startDate, endDate=endDate)
totalBayList = generateMaintenanceData(numBays=5, startDate=startDate, endDate=endDate, maintenanceList=maintenanceList)

header = ["Date", "EquipmentID", "Class", "Model", "In Use?", "Repaired?", "RepairReason", "Avg Load Time (min)", "Average Unload Time (min)", "Average Load Wait Time (min)", "Average Unload Wait Time (min)", "Average Cycle Time (min)", "Time to Repair (min)", "Repair Cost", "Maintenance Cost", "Payload (kg)", "Net Payload Worth", "Cost of Truck"]

# open the file in the write mode
with open('truck_data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)
    
    for truck in totalTruckList:
      # write multiple rows
      writer.writerows(truck)

header = ["Date", "BayID", "In Use?", "Total Number of Maintenance Jobs", "Number of Maintenance Jobs Completed", "Maintenance Job Backlog"]

# open the file in the write mode
with open('bay_data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)
    
    for bay in totalBayList:
      # write multiple rows
      writer.writerows(bay)