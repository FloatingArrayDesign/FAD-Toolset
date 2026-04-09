# Platform Class

The Platform class represents a floating offshore structure (FOWT, substation, WEC, etc.) in the array. It contains properties and methods relating to a moored floating platform and stores information on connected Edge objects (mooring lines, cables).

Currently, RAFT information on the specific geometry and hydrostatic properties of the platform are not stored in the platform object. When a project is initialized, a RAFT model is created if directed to, and this information is stored in the RAFT model found in project.array.

**Parent Class**: Node
## Platform Properties

### Geometric & Positioning Properties

- **r** - coordinates of platform center `[x, y, z]` [m]. Defines reference point for all platform-centric calculations
- **phi** - Heading angle [rad], clockwise positive
- **rFair** - Fairlead radius (radial distance from platform center to fairlead attachment points) [m]
- **zFair** - Fairlead depth below water surface [m]
- **rc** - Grid array location as `[row, column]`

### Design & Configuration Properties

- **dd** - Design dictionary
- **entity** - Platform type: 'FOWT', 'Substation', 'WEC', or user-defined string
- **id** - Unique platform identifier
- **body** - Associated MoorPy Body object (auto-populated by project.getMoorPyArray())

### Analysis & Results Properties

- **envelopes** - Dictionary of motion envelopes. Watch circle envelopes auto-populated by project.arrayWatchCircle() or platform.getWatchCircle(). Each entry is a dict with x,y or shape
- **x_ampl** - Wave-frequency motion amplitude about mean [m]
- **mean_loads** - Dictionary of external loads: 'current', 'wind', 'thrust', 'waves' [N]
- **raftResults** - Dictionary containing RAFT frequency-domain analysis results for this platform

### Environmental & Cost Properties

- **cost** - Dictionary breaking down platform costs [USD]
- **reliability** - Dictionary of platform reliability metrics
- **failure_probability** - Dictionary of failure probability estimates


## Platform Methods

### Positioning & Geometry Management

#### setPosition()
Set the platform location and optionally update its heading. Automatically updates all connected mooring, cable, and anchor end positions.

#### updateMooringPoints()
Update end positions of all attached moorings based on fairlead configuration. Called automatically by `setPosition()`.

### Connection Management

#### getMoorings()
Return dict containing all Mooring objects attached to this platform.
keys are mooring ids, values are mooring objects.


#### getCables()
Return dict containing all Cable objects connected to this platform.


#### getAnchors()
Return dict containing all Anchor objects associated with this platform's mooring system.


### Analysis Methods

#### getWatchCircle()
Compute platform's motion envelope (watch circle) for given thrust. Calculates mooring line tensions, safety factors, cable sag, and seabed disturbance.

#### getBufferZones()
Calculate safety buffer zones around mooring lines and anchors for cable routing validation.

#### mooringSystem()
Create standalone MoorPy system for this platform (different from project-level system). Stored as platform.ms

#### calcThrustTotal()
Sum thrust forces from all attached turbines.

---

## Fairlead Class

The Fairlead class represents mooring line attachment points on platforms.

**Parent Classes**: Node, dict

### Fairlead Properties

No additional properties or methods beyond those in the base Node class.


---

## Common Use Cases

### Check Platform Stationkeeping
```python
platform = project.platformList['Platform_01']
moorings = platform.getMoorings()
thrust = platform.calcThrustTotal()
platform.getWatchCircle(thrust, include_dyn_amp=True)
project.plot2d() # plot to see motion envelopes
```

### Array Repositioning
```python
spacing = 600  # [m]
for i, platform in enumerate(project.platformList.values()):
    x = i * spacing
    platform.setPosition([x, 0.0], heading=0.0)
```
