# Zavrsni rad - Tin Jukic
# Vehicle Routing Problem (VRP)
import numpy as np

import tensorflow as tf
import pygad
import pygad.kerasga

import Utils
from Utils import *
import numpy


# Moj model ce imati input layer s brojem izlaz koliko ima i odredista, 3 hidden layer-a, svaki s brojem izlaza
# jednakim kao i brojem ulaza (broj ulaza koliko prethodni layer ima izlaza) te output layer koji ce imati broj
# izlaza koliko ima auta u mrezi, a broj ulaza ce biti jednak jednak broju izlaza prethodnog sloja Ulazni podaci za
# input layer ce biti podaci o udaljenostima izmedju pojedinih gradova Izlazni podaci ce biti ocjena pojedine rute


def fitnessFunc(solution, solutionIndex) -> float:
    print("FITNESS")
    # fitnessFunc ce racunati kvalitetu rjesenja
    # UCS rjesenje uz neke promjene -> neuronska mi mora ocijeniti na neki nacin rjesenje s model.predict()

    print(f"Solution index: {solutionIndex}")
    print(solution)

    # OVDJE IDE UCS ALGORITAM KOJI RADI UZ POMOĆ NEURONSKE MREŽE
    global keras_ga, model, dataModel

    fitness = 0.0

    # UCS uz poziv evaluate funkcije za neuronsku mrežu
    data = dataModel
    vehicles = []
    for i in range(data["numOfVehicles"]):
        vehicles.append(Vehicle())

    while True:
        finished = False

        for i in range(len(vehicles)):
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
            findNodeToVisitNNResult = findNodeToVisitNN(vehicle=vehicle, currentNodeIndex=currentNodeIndex, data=data, model=model)
            nodeToVisitIndex = findNodeToVisitNNResult["minDistanceNodeIndex"]
            while nodeToVisitIndex != -1:
                # potrebno je resetirati j, kako bi pretraga mogla krenuti od pocetka
                # takodjer je potrebno reci da je trenutni cvor taj novi cvor u koji idem
                # treba azurirati potrebne liste i kapacitet auta
                currentNodeIndex = nodeToVisitIndex
                findNodeToVisitNNResult = findNodeToVisitNN(vehicle=vehicle, currentNodeIndex=currentNodeIndex,
                                                            data=data, model=model)
                nodeToVisitIndex = findNodeToVisitNNResult["minDistanceNodeIndex"]
                fitness += findNodeToVisitNNResult["evaluation"]

            # gotov si s tim autom
            vehicle.capacity -= calculateDistance(currentNode, data["coordinates"][data["depotIndex"]])
            vehicle.traveledDistance += calculateDistance(currentNode, data["coordinates"][data["depotIndex"]])

            # iskoristio si sve aute koje imas na raspolaganju
            if i == data["numOfVehicles"] - 1 and finished == False:
                finished = True

        if finished:
            print("FINISHED")
            Utils.reset(data=data)
            break

    print(f"Current fitness: {fitness}")

    arr = 1.0 / numpy.abs(fitness + 0.000001)
    print(arr[0].astype(np.float))

    return float(arr[0].astype(np.float))


def callbackFunc(ga_instance):
    return


# tf.export CUDA_VISIBLE_DEVICES=0
print(tf.test.is_gpu_available())
# def start():
# pravljenje data modela
dataModel: dict = createDataModel()  # dictionary koji sadrzi podatke o modelu

gpus = tf.config.list_physical_devices('GPU')
if gpus:
  try:
    # Currently, memory growth needs to be the same across GPUs
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    logical_gpus = tf.config.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Memory growth must be set before GPUs have been initialized
    print(e)

# pravljenje pojedinih layera za neuronsku mrezu
inputLayer = keras.layers.Input(shape=(1,))
hiddenLayer1 = keras.layers.Dense(4, activation="relu")(inputLayer)
hiddenLayer2 = keras.layers.Dense(8, activation="relu")(hiddenLayer1)
outputLayer = keras.layers.Dense(1, activation="linear")(hiddenLayer2)
numOfSolutions = 3

print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

model = keras.Model(inputs=inputLayer, outputs=outputLayer)
print(model.summary())
keras_ga = pygad.kerasga.KerasGA(model=model, num_solutions=numOfSolutions)

numOfGenerations = 5
numParentsMating = 2
initialPopulation = keras_ga.population_weights

gaInstance = pygad.GA(num_generations=numOfGenerations, num_parents_mating=numParentsMating,
                      initial_population=initialPopulation, fitness_func=fitnessFunc,
                      on_generation=callbackFunc)
gaInstance.run()
gaInstance.plot_fitness(title="VRP - ANN & GA", linewidth=4)

solution, solutionFitness, solutionIndex = gaInstance.best_solution()
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solutionFitness))
print(f"Index of the best solution: {solutionIndex}".format(solution_idx=solutionIndex))

# dohvati weights za bestSolution i kasnije modeliraj s njim problem
bestSolutionWeights = pygad.kerasga.model_weights_as_matrix(model=model, weights_vector=solution)
file = open("bestSolutionWeights.txt", "w")
for weight in bestSolutionWeights:
    file.write(str(weight) + ", ")
file.close()
print(f"Weights for the best solution are: {bestSolutionWeights}")

model.set_weights(bestSolutionWeights)
Utils.bestSolutionVRP(data=dataModel, model=model)


# if __name__ == '__main__':
#     print("Solving Vehicle Routing Problem (VRP) using Artificial Neural Network (ANN) with Genetic Algorithm (GA)")
#     start()
#     print("Solving finished!")
