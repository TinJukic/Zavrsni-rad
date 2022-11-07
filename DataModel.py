# Solomon data model

from VRPClasses import *


def createDataModel():
    data = {}

    # read data from file
    dataFile = open("solomon-100/In/r101.txt", "r")
    line = dataFile.readline()

    for i in range(9):
        line = dataFile.readline()

    data["coordinates"] = []
    while line:
        splitLine = line.split(None)
        data["coordinates"].append(
            Coordinates(int(splitLine[0]), int(splitLine[1]), int(splitLine[2]), int(splitLine[3])))
        line = dataFile.readline()

    data["depotIndex"] = 0
    data["numOfLocations"] = len(data["coordinates"])
    data["numOfVehicles"] = 25
    data["visitedNodes"] = []  # bit ce spremljeni indexi obidjenih cvorova

    dataFile.close()

    return data
