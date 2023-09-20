# Este archivo implementa la simulacion del algoritmo de 
# recorrido en profundidad de Awerbuch

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

class AlgorithmDFS(Model):
    # Esta clase desciende de la clase Model e implementa los metodos
    # "init()" y "receive()", que en la clase madre se definen como abstractos
  
    def init(self):
        # Aqui se definen e inicializan los atributos particulares del algoritmo
        print("Inicio funciones", self.id)

        #se inicializa el arreglo de banderas
        self.banderas = {}
        print("Mis vecinos son: ", end=" ")
        for neighbor in self.neighbors:
            #inicialmente en falso==0; verdadero==1
            self.banderas[neighbor] = 0
            print(neighbor, end=" ")
        print("\n")
        #print(banderas)

        self.father = self.id
        self.unvisited = self.neighbors

    def receive(self, event):
        # Aqui se definen las acciones concretas que deben ejecutarse cuando se
        # recibe un evento
        print("T = ", self.clock, " Nodo [", self.id, "] Recibo :", event.getName(), "desde [", event.getSource(), "]")
        print("Nodo [", self.id, "] Mi lista de no visitados es: ", self.unvisited)

        #al recibir INICIA
        if event.getName() == "INICIA":
            #Para cada vecino
            for neighbor in self.unvisited:
                # envia VISITADO a neighbor
                newevent = Event("VISITADO", self.clock + 1.0, neighbor, self.id)
                self.transmit(newevent)
                # y pone en verdadero la bandera correspondiente
                self.banderas.update({neighbor: 1})

        #al recibir DESCUBRE
        elif event.getName() == "DESCUBRE":
            #asigna al nodo transmisor como su padre
            self.father = event.getSource()
            #y para cada vecino
            for neighbor in self.unvisited:
                if neighbor != self.father:
                    #envia VISITADO a neighbor
                    newevent = Event("VISITADO", self.clock + 1.0, neighbor, self.id)
                    self.transmit(newevent)
                    #y pone en verdadero la bandera correspondiente
                    self.banderas.update({neighbor: 1})
            #pero si ya no tiene vecinos mas que el nodo que le envio el descubre
            if len(self.unvisited) != 0:
                #envia REGRESA al transmisor
                newevent = Event("REGRESA", self.clock + 1.0, event.getSource(), self.id)
                self.transmit(newevent)
        #al recibir VISITADO
        elif event.getName() == "VISITADO":
            # se elimina el nodo transmisor de la lista de nodos sin_visitar del receptor
            self.unvisited.remove(event.getSource())
            #y envia ACK al transmisor
            newevent = Event("ACK", self.clock + 1.0, event.getSource(), self.id)
            self.transmit(newevent)
        #al recibir ACK
        elif event.getName() == "ACK":
            #pone la bandera del transmisor en falso (==0)
            self.banderas.update({event.getSource(): 0})
            #si recibe ACK de todos sus vecinos, se autoenvia REGRESA
            regresa = all(bandera == 0 for bandera in self.banderas.values())
            if regresa == True:
                newevent = Event("REGRESA", self.clock + 1.0, self.id, self.id)
                self.transmit(newevent)
        #al recibir REGRESA
        elif  event.getName() == "REGRESA":
            #si existen vecinos sin visitar
            if len(self.unvisited) != 0:
                #les envia DESCUBRE
                for neighbor in self.unvisited:
                    #y los quita de la lista sin_visitar
                    self.unvisited.remove(neighbor)
                    print("Nodo [", self.id, "] Mi lista de no visitados es: ", self.unvisited)
                    #envia DESCUBRE a neighbor
                    newevent = Event("DESCUBRE", self.clock + 1.0, neighbor, self.id)
                    self.transmit(newevent)
            #si no tiene vecinos sin visitar y si no es el nodo raiz,
            else:
                #envia REGRESA a padre
                newevent = Event("REGRESA", self.clock + 1.0, self.father, self.id)
                self.transmit(newevent)

# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------
# construye una instancia de la clase Simulation recibiendo como parametros el nombre del 
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion

if len(sys.argv) != 2:
    print("Por favor dame el nombre del archivo con la grafica de comunicaciones")
    raise SystemExit(1)

maxtime= 100
experiment = Simulation(sys.argv[1], maxtime)#filename, maxtime

# imprime lista de nodos que se extraen del archivo
# experiment.graph[indice+1 == nodo] == vecino
print("Lista de nodos: ", experiment.graph)

# asocia un pareja proceso/modelo con cada nodo de la grafica
for i in range(1,len(experiment.graph)+1):
    m = AlgorithmDFS()
    experiment.setModel(m, i)

# inserta un evento semilla en la agenda y arranca
seed = Event("INICIA", 0.0, 1, 1)#name, time, target, source
experiment.init(seed)
experiment.run()
