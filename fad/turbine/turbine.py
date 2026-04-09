# class for wind turbine

import numpy as np

from fad.seabed_tools import interpFromGrid
from fad.famodel_base import Node
from copy import deepcopy


class Turbine(Node):
    '''
    Class for Turbine - used for holding design info and making lookup
    table of thrust force for different conditions. This would typically
    be an entry in a Project turbineTypes list (one per turbine type).
    '''
    
    def __init__(self, dd, id, D=242, rated_wind_speed=10.59, rho_air=1.225,
                 rho_water=1025, mu_air=1.81e-5, shearExp_air=.11):
        '''
        Initialize turbine object based on dictionary from ontology or RAFT
        input file.
        
        Parameters
        ----------
        dd : dict
            Dictionary describing the design, in RAFT rotor format.
        '''
        Node.__init__(self, id) # initialize node base class
        
        
        # Design description dictionary for this Turbine
        self.dd = deepcopy(dd)
        self.dd['rho_air'] = rho_air
        self.dd['rho_water'] = rho_water
        self.dd['mu_air'] = mu_air
        self.dd['shearExp_air'] = .11
        
        self.D = D # rotor diameter [m]

        # Dictionaries for addition information
        self.loads = {}
        self.reliability = {}
        self.cost = {}
        self.failure_probability = {}
        self.thrust = 0
        
        try:
            self.makeRotor()
        except:
            print('Could not successfully create rotor.')
        else:
            self.calcThrustForces(U0=rated_wind_speed)
    
    
    def makeRotor(self):
        '''
        Create a RAFT Rotor object for the turbine.
        '''
        
        from raft.raft_rotor import Rotor
        
        # Make RAFT Rotor based on dd with no frequencies and rotor index 0
        self.dd['nrotors'] = 1
        
        self.rotor = Rotor(self.dd, [], 0)
        
    
    def calcThrustForces(self, U0=10.59):
        '''
        Compute thrust force vector.
        '''
        
        loads, derivs = self.rotor.runCCBlade(U0)
            
        self.thrust = loads['T'][0]

