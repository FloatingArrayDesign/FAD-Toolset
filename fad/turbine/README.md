# The Turbine Class
The turbine class contains properties and structures related to a turbine, for example a wind or water turbine. This class inherits from the Node class.

## Turbine Class Properties
- dd : design description dictionary
- D  : rotor diameter of turbine
- loads : dictionary of loads on the turbine
- reliability : dictionary of turbine reliability factors
- cost : dictionary of turbine costs
- failure_probability : dictionary of turbine failure probabilities
- thrust : maximum thrust force on the turbine

## Turbine Class Methods
- makeRotor(): creates a RAFT rotor object for the turbine
- calcThrustForces(): computes and stores the thrust force of the turbine based on rated speed