# Moorings, Sections, and Connectors

This file contains information on Mooring class and the subcomponent classes, Section and Connector.
The layout of this file is as follows:
## Layout
* [The Mooring Class](#the-mooring-class)
	* [Mooring Properties](#mooring-properties)
	* [Mooring Methods](#mooring-methods)
* [The Section Class](#the-section-class)
* [The Connector Class](#the-connector-class)


## The Mooring Class

The Mooring class provides a data structure for design information of a mooring line. Design information 
includes a design dictionary with the following details:
- Anchoring radius
- Anchor depth
- Fairlead radius
- Fairlead depth 
- Detail on each line section
	- Line section type
		- diameter (nominal and volume-equivalent)
		- material
		- cost
		- mass
		- MBL
		- EA
	- Line section length
	
The Mooring object contains subcomponent objects that represent each component of the full mooring line. Line segments are Section objects, while connectors between segments and at the ends of the lines are Connector objects. These segments alternate.

## Mooring Properties

## Mooring methods

### createSubsystem

Create a MoorPy subsystem for a line configuration from the design dictionary. Regular or suspended lines 
may be used.

### getCost

Obtain the total cost of the mooring line

### setEndPosition

Set the position of an end of the mooring line.

### reposition

Adjust the mooring position based on changed platform location or heading. It can call a custom "adjuster" 
function if one is provided. Otherwise it will just update the end positions.


## Anchor methods

### makeMoorPyAnchor

Create a MoorPy point object that contains the anchor design information in a MoorPy system.

### getMPForces

Find forces on the anchor using MoorPy Point.getForces method and store in loads dictionary

### getCost

Find costs of the anchor from MoorProps and store in design dictionary

### getMass

Find mass and/or UHC of the anchor from MoorProps and store in design dictionary

## The Connector Class

The Connector class provides a data structure for design information of a connector. The design dictionary includes
the following details: 
- connector type
	- mass
	- volume 
	- CdA
	
The connector class also contians an xyz location of the connector, and a connector object in MoorPy.

## Connector methods

### makeMoorPyConnector

Create a MoorPy connector object in a MoorPy system. Mass, volume, and CdA are added as available in the design dictionary.