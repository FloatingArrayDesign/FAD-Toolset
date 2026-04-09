# FAD-Toolset Examples

This folder contains examples for various functionalities of FAD-Toolset.
These examples are designed to help users get acquainted with the package and how it can be used.
The sample .yaml files may also be used as templates for the user's own floating array ontologies.
The examples are described below:

## Numbered Examples

The numbered example folders (01-10) contain small isolated examples showing ontologies and driver files for basic functionalities. Within each folder, a number of sub-functionalities are shown individually.
The numbered example folders are as follows:
- 01_Visualization : 2D and 3D plotting of various components and array information
- 02_Mooring_Analysis_MoorPy : Run and analyze mooring and cable simulations
- 03_Frequency_Domain_Analysis_RAFT : Run and analyze floating platform/ floating wind simulations, store outputs in an excel file
- 04_Geography : Load and set up geographical information such as soils, bathymetry, lease coordinates, etc
- 05_Anchor_Capacity_and_Sizing : Calculate anchor capacity and size anchors to meet safety requirements
- 06_Design : Examples of the design subpackage (LineDesign, layout optimization, including cable routing and re-routing to avoid obstacles)
- 07_Cost_Analysis : Calculate total cost of array components, print out breakdown of costs
- 08_Design_Adjustment : Include specified fairleads, j-tubes, and rotate arrays
- 09_Manual_Setups : Methods for manually creating array (e.g. from a MoorDyn file)
- 10_Misc : miscellaneous examples of more niche features, such as shared moorings, uniform arrays, etc

## FAD-Toolset project from a yaml file example
This example shows how to make an FAD-Toolset Project from a yaml file. The sample shows various possibilities for mooring and anchoring including shared moorings and shared anchors. It also shows some functionalities of the floating array model including:
- integration with MoorPy
- integration with RAFT
- integration with FLORIS for AEP calculations
- adding marine growth to moorings and cables
- calculating capacity, loads, and safety factors on an anchor
- determining the watch circle of a platform, with maximum tensions and minimum safety factors for all mooring lines and cables attached to the platform
- plotting the 2d plan view of a farm, including: 
    - bathymetry
    - boundaries 
    - mooring lines, cables (including routing), platforms, and substations
    - motion envelopes for mooring lines and platforms
- plotting the 3d view of a farm, including: 
    - bathymetry
    - boundaries
    - mooring lines, platforms, and substations
    - dynamic cables
    - static cables, including burial depth and routing

## Common Inputs Folder
The common inputs folder contains input files that are used by different examples
