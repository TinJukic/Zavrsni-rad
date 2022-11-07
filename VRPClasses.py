# Classes for VRP
import VRPClasses


class Vehicle:
    def __init__(self):
        self.capacity = 200
        self.traveledDistance = 0
        self.usedCapacity = 0
        self.path = []  # spremam index cvora koji je obisao


class Coordinates:
    def __init__(self, number, x, y, demand):
        self.obisao = False
        self.number = number
        self.x = x
        self.y = y
        self.demand = demand

    def getNumber(self):
        return self.number

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getDemand(self):
        return self.demand

    def getObisao(self):
        return self.obisao

    def __eq__(self, other):
        return self.number == other.number
