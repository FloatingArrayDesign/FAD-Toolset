# Floating Array Design Toolset

The Floating Array Design (FAD) Toolset is a collection of tools for
modeling and designing arrays of floating offshore structures. It was
originally designed for floating wind systems but has applicability
for many offshore applications.

A core part of the FAD Toolset is the floating array model,
which serves as a high-level library for efficiently
modeling a floating array, such as a floating wind array. It combines site condition information and a 
description of the floating array design, and contains functions for evaluating
the array's behavior considering the site conditions. For example, it combines
information about site soil conditions, mooring line loads, and an array's anchor characteristics to
estimate the holding capacity of each anchor. 

The library works in conjunction with the tools RAFT, MoorPy, and FLORIS to model floating
platforms, wind turbines, mooring systems, power cables, and array wakes respectively.

Layered on top of the floating array model is a set of design tools that can
be used for algorithmically adjusting or optimizing parts of the a floating
array. Specific tools existing for mooring lines, shared mooring systems, 
dynamic power cables, static power cable routing, and overall array layout.
These capabilities work with the design representation and evaluation functions
in the floating array model, and they can be applied by users in various combinations to suit
different purposes. 

In addition to standalone uses of the FAD Toolset, a coupling has been made with
[Ard](https://github.com/WISDEM/Ard), a sophisticated and flexible wind farm
optimization tool. This coupling allows Ard to use certain mooring system
capabilities from FAD to perform layout optimization of floating wind farms
with Ard's more advanced layout optimization capabilities.

The FAD Toolset works with the [IEA Wind Task 49 Ontology](https://github.com/IEAWindTask49/Ontology),
which provides a standardized format for describing floating wind farm sites
and designs. 

See example use cases in our [examples](./examples/README.md) folder.

For working with the library, it is important to understand the floating array 
model structure, which is described more [here](./fad/README.md).


## Installation

FAD-Toolset is built entirely in Python. It is recommended that users familiarize themselves with Python and install Python onto their machine through Anaconda or Miniconda distributions.

The following describes the steps to set up a python virtual environment, install FAD-Toolset, and all install required dependencies into the environment.

First, in a terminal such as the Anaconda Powershell Prompt, clone the GitHub repository to access the files. Navigate to a directory of your choice to download the repository and then navigate into the FAD-Toolset folder.

```
(base) YOUR_PATH> git clone https://github.com/FloatingArrayDesign/FAD-Toolset.git
(base) YOUR_PATH> cd FAD-Toolset
```

Next, create a new python virtual environment with an environment name of your choice. We will use 'fad-env' as an example.

```
(base) YOUR_PATH\FAD-Toolset> conda env create -n fad-env -f fad-env.yaml
(base) YOUR_PATH\FAD-Toolset> conda activate fad-env     # run `conda deactivate` to deactivate
(fad-env) YOUR_PATH\FAD-Toolset>
```

Within the new python virtual environment, we can install FAD-Toolset. 

Use ```pip``` to install the contents of this folder. Ensure you are still within the root directory of FAD-Toolset.

```
(fad-env) YOUR_PATH\FAD-Toolset> pip install -e .
```

This command tells `pip` to look at the `pyproject.toml` file to install the FAD-Toolset program into the current virtual environment, along with all the dependencies listed in the `pyproject.toml` file. There is overlap between the python packages listed in the `pyproject.toml` and the `fad-env.yaml` file since the installation can be done by either or both of the package installation managers, `conda` and `pip`. Specific versions of packages like scipy are listed in the `pyproject.toml` file to ensure they get installed properly. The `-e` option allows users to make local changes to their FAD-Toolset files and have those changes be reflected in the FAD-Toolset installation.

Lastly, we can test the installation by running `pytest` from the main FAD-Toolset directory.

```
(fad-env) YOUR_PATH\FAD-Toolset> pytest
```

<!-- FAD requires MoorPy and we currently install it separately. If you don't already have it,
you can install MoorPy with ```git clone https://github.com/NREL/MoorPy.git```
then navigate to the MoorPy folder and install with ```pip install .```.
Make sure your virtual enviroment is activated before installing MoorPy. -->

For future changes to dependencies like MoorPy or RAFT, as long as those changes come through a new release of the software and an updated version is listed on PyPI, users should manually re-install the dependencies in their virtual environment to gather those new changes (i.e., `pip install moorpy`).

FAD-Toolset is also pip installable and can be installed using `pip install fad-toolset`. The main source code folder in the repo is named `fad`, which is how classes and functions will be imported (i.e., `import fad.Project as Project` or `from fad.anchors.anchor import Anchor`).



### Installation/Dependency Issues

Some of the toolset's functionality requires RAFT, which in turn requires
CCBlade, which recently can only be installed as part of WISDEM. Some issues
can occur from the associated dependencies, but some have quick fixes:

- Getting a readline error when breakpoint() is called?  Check if the 
  pyreadline3 package is installed in the conda environment. If so, try
  removing it.

- Wanting to use both WEIS and FAD Toolset in the same environment, but
  getting errors related to "smt" when installing WEIS? Try commenting out
  the smt requirement in environment.yml and pyproject.toml.


## Subpackages

The library has a core Project class for organizing information, classes for each component of an array and an evolving
collection of subpackages for specific functions. The current subpackages are:

- anchors: contains modules for anchor capacity calculations, in addition to the anchor class
- failures: contains modules for failure modeling with graph theory, and allows for enactment of a failure mode.
- seabed: contains modules for seabed bathymetry and boundary information
- design: contains various tools for performing design steps.

Please navigate into the subfolders above for additional information.


## Getting Started

The easiest way to create a FAD project is to provide the array 
information in an ontology yaml file. FAD has been designed
to work with a specific ontology yaml setup, which is described 
in detail in the [Ontology ReadMe](./fad/ontology/README.md).

For examples of ontologies and driver files of common use cases, 
we recommend starting with the numbered examples in the examples folder.
The [visualization examples](./examples/01_Visualization/) are a good place
to start. Run the .py files and inspect the .yaml files with the same name 
to see what information is required for different uses and how they are conveyed
in the ontology.

To see an example with all use cases, the [example driver file](./examples/example_driver.py) creates a FAD Project 
object from a pre-set ontology file and shows the syntax and outputs of 
various capabilities. For guidance on creating your own ontology yaml file, 
it is recommended to read through the [Ontology ReadMe](./fad/ontology/README.md), 
then either adapt one of the ontology samples or fill in the ontology template. 

The [core model readme](./fad/README.md) describes the Project class structure, 
as well as the properties and methods of each component class. 

There are some limited helper functions to automatically fill in sections 
of a yaml from a MoorPy system or a list of platform locations. 
See [helpers](./fad/helpers.py) for the full list of yaml writing capabilities. 


## Authors

The NREL Floating Wind Array Design team.