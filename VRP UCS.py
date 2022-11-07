# Tin Jukić, završni rad
# UCS implementation of the VRP

from Utils import *


def ucs():
    data = createDataModel()
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
            nodeToVisitIndex = findNodeToVisit(vehicle=vehicle, currentNodeIndex=currentNodeIndex, data=data)
            while nodeToVisitIndex != -1:
                # potrebno je resetirati j, kako bi pretraga mogla krenuti od pocetka
                # takodjer je potrebno reci da je trenutni cvor taj novi cvor u koji idem
                # treba azurirati potrebne liste i kapacitet auta
                currentNodeIndex = nodeToVisitIndex
                nodeToVisitIndex = findNodeToVisit(vehicle=vehicle, currentNodeIndex=currentNodeIndex, data=data)

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


if __name__ == '__main__':
    print("Zapocinjem izvrsavanje UCS algoritma za VRP.")
    print()
    ucs()
