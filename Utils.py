# Utils for VRP

import math

import keras

import VRPClasses
from DataModel import *
import tensorflow


def calculateDistance(c1: Coordinates, c2: Coordinates):
    return math.sqrt(math.pow((c2.getX() - c1.getX()), 2) + math.pow((c2.getY() - c1.getY()), 2))


def findNodeToVisit(vehicle: Vehicle, currentNodeIndex: int, data: dict):
    minDistanceNodeIndex = -1
    currentNode: VRPClasses.Coordinates = data["coordinates"][currentNodeIndex]

    cannotVisitNodes: [VRPClasses.Coordinates] = []

    for i in range(data["numOfLocations"]):
        node = data["coordinates"][i]  # cvor za koji se provjerava mozes li ga obici

        if cannotVisitNodes.__contains__(node):
            continue

        # ako je cvor vec obidjen, preskoci ga ili ako je cvor pocetni (depot) ili ako je to trenutni cvor
        if node.obisao == True or i == data["depotIndex"] or i == currentNodeIndex:
            continue

        distanceToTravel = calculateDistance(currentNode, node)
        nodeDemand = currentNode.getDemand()
        currentVehicleCapacity = vehicle.capacity
        shouldReset = False

        for j in range(i + 1, data["numOfLocations"], 1):
            nextNode: VRPClasses.Coordinates = data["coordinates"][j]
            nextNodeDistance = calculateDistance(nextNode, node)

            if nextNode.obisao == True or j == data["depotIndex"] or j == currentNodeIndex:
                continue

            if nextNodeDistance < distanceToTravel:
                i = j - 1
                shouldReset = True
                break
            else:
                continue

        if shouldReset:
            continue

        if currentVehicleCapacity - nodeDemand >= 0:
            distance = calculateDistance(currentNode, node)
            vehicle.capacity -= nodeDemand
            vehicle.traveledDistance += distance
            vehicle.usedCapacity += nodeDemand
            vehicle.path.append(i)
            data["visitedNodes"].append(i)  # dodaj node u listu obidjenih nodeova
            node.obisao = True  # obiljezi da si obisao taj node
            minDistanceNodeIndex = i
            break
        else:
            cannotVisitNodes.append(node)

    return minDistanceNodeIndex


def findNodeToVisitNN(vehicle: Vehicle, currentNodeIndex: int, data: dict, model) -> dict:
    print(f"Evo usao sam tu s trenutnim node indexom: {currentNodeIndex}")

    minDistanceNodeIndex = -1
    currentNode: VRPClasses.Coordinates = data["coordinates"][currentNodeIndex]

    result = {
        "minDistanceNodeIndex": minDistanceNodeIndex,
        "evaluation": 0.0
    }

    cannotVisitNodes: [VRPClasses.Coordinates] = []

    for i in range(data["numOfLocations"]):
        node = data["coordinates"][i]  # cvor za koji se provjerava mozes li ga obici

        if cannotVisitNodes.__contains__(node):
            continue

        # ako je cvor vec obidjen, preskoci ga ili ako je cvor pocetni (depot) ili ako je to trenutni cvor
        if node.obisao == True or i == data["depotIndex"] or i == currentNodeIndex:
            continue

        # neuronska mreža treba ocijeniti izabrani node te na osnovu te ocjene odlučiti koji node obići idući

        distanceToTravel = calculateDistance(currentNode, node)
        nodeDemand = currentNode.getDemand()

        # ovdje treba ocijeniti rjesenje pomocu neuronske mreze
        tfDistanceToTravel = tensorflow.expand_dims(distanceToTravel, axis=0)
        tfNodeDemand = tensorflow.expand_dims(nodeDemand, axis=0)
        evaluationForNode = model.predict(tfNodeDemand)[0]

        currentVehicleCapacity = vehicle.capacity
        shouldReset = False

        for j in range(i + 1, data["numOfLocations"], 1):
            nextNode: VRPClasses.Coordinates = data["coordinates"][j]
            nextNodeDistance = calculateDistance(nextNode, node)

            nextNodeEvaluation = model.predict(tensorflow.expand_dims(nextNode.getDemand(), axis=0))[0]

            if nextNode.obisao == True or j == data["depotIndex"] or j == currentNodeIndex:
                continue

            if nextNodeDistance < distanceToTravel and nextNodeEvaluation < evaluationForNode:
                i = j - 1
                shouldReset = True
                break
            else:
                continue

        if shouldReset:
            continue

        if currentVehicleCapacity - nodeDemand >= 0:
            distance = calculateDistance(currentNode, node)
            vehicle.capacity -= nodeDemand
            vehicle.traveledDistance += distance
            vehicle.usedCapacity += nodeDemand
            vehicle.path.append(i)
            data["visitedNodes"].append(i)  # dodaj node u listu obidjenih nodeova
            node.obisao = True  # obiljezi da si obisao taj node
            minDistanceNodeIndex = i
            result["minDistanceNodeIndex"] = minDistanceNodeIndex
            result["evaluation"] = evaluationForNode
            print(f"Izabrao sam node s indexom: {minDistanceNodeIndex}")
            break
        else:
            cannotVisitNodes.append(node)

    return result


def bestSolutionVRP(data: dict, model):
    print("Solving VRP with the best found solution.")

    vehicles = []
    for i in range(data["numOfVehicles"]):
        vehicles.append(Vehicle())

    while True:
        finished = False

        for i in range(len(vehicles)):
            print(f"Trenutno sam na autu broj: {i + 1}")

            vehicle = vehicles[i]
            currentNodeIndex = data["depotIndex"]  # svaki auto krece od depota
            currentNode = data["coordinates"][currentNodeIndex]

            if len(data["visitedNodes"]) == (data["numOfLocations"] - 1):
                # obisao si sve cvorove ili si potrosio sve aute...
                finished = True
                break

            # ako je cvor potrebno obici, pokreni racunanje cijena svih cvorova za njega
            # za pocetak preskoci depot cvor
            # kada nadjes cvor s najmanjom cijenom, provjeri moze li se njima doci i do depota
            # ako moze, uzmi ga
            # ako ne, odi do depota i reci da se taj auto vise ne moze koristiti
            # potrebno je stalno azurirati kapacitet auta
            nodeToVisitIndex = findNodeToVisitNN(vehicle=vehicle, currentNodeIndex=currentNodeIndex, data=data, model=model)["minDistanceNodeIndex"]
            while nodeToVisitIndex != -1:
                # potrebno je resetirati j, kako bi pretraga mogla krenuti od pocetka
                # takodjer je potrebno reci da je trenutni cvor taj novi cvor u koji idem
                # treba azurirati potrebne liste i kapacitet auta
                currentNodeIndex = nodeToVisitIndex
                nodeToVisitIndex = findNodeToVisitNN(vehicle=vehicle, currentNodeIndex=currentNodeIndex, data=data, model=model)["minDistanceNodeIndex"]

            # gotov si s tim autom
            print("Niti jedan cvor ne mozes obici, odi u depot")
            vehicle.capacity -= calculateDistance(currentNode, data["coordinates"][data["depotIndex"]])
            vehicle.traveledDistance += calculateDistance(currentNode, data["coordinates"][data["depotIndex"]])

            # iskoristio si sve aute koje imas na raspolaganju
            if i == data["numOfVehicles"] - 1 and finished == False:
                finished = True

            print()

        if finished:
            # ispisi put za svaki auto
            vehicleNum = 0
            for vehicle in vehicles:
                vehicleNum += 1
                print(f"Vehicle number: {vehicleNum}:")
                print(f"Traveled distance: {vehicle.traveledDistance}")
                print(f"Remaining capacity: {vehicle.capacity}")
                print(f"Used capacity: {vehicle.usedCapacity}")
                print(f"Visited customers: {len(vehicle.path)}")
                print("Route", end=": ")
                for p in vehicle.path:
                    if vehicle.path[len(vehicle.path) - 1] == p:
                        print(p)
                    else:
                        print(p, end=" -> ")
                print()
                if len(vehicle.path) == 0:
                    print()
            break
        else:
            print("Something went wrong and UCS algorithm for VRP did not finish!")
            break


def reset(data: dict):
    print("Reset data for next generation...")

    data["visitedNodes"] = []
    for (coordinate) in data["coordinates"]:
        coordinate: Coordinates
        coordinate.obisao = False

    print("Reset completed")
