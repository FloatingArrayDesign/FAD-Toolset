"""A set of functions for processing seabed information for a Project."""


import os
import matplotlib.pyplot as plt
import numpy as np






def readBathymetryFile(filename, dtype=float):

    with open(filename, 'r') as f:
        # skip the header
        line = next(f)
        # collect the number of grid values in the x and y directions from the second and third lines
        line = next(f)
        nGridX = int(line.split()[1])
        line = next(f)
        nGridY = int(line.split()[1])
        # allocate the Xs, Ys, and main bathymetry grid arrays
        bathGrid_Xs = np.zeros(nGridX)
        bathGrid_Ys = np.zeros(nGridY)
        bathGrid = np.zeros([nGridY, nGridX], dtype=dtype)  # MH swapped order June 30
        # read in the fourth line to the Xs array
        line = next(f)
        bathGrid_Xs = [float(line.split()[i]) for i in range(nGridX)]
        strlist = []
        # read in the remaining lines in the file into the Ys array (first entry) and the main bathymetry grid
        for i in range(nGridY):
            line = next(f)
            entries = line.split()
            bathGrid_Ys[i] = entries[0]
            if dtype==float:
                bathGrid[i,:] = entries[1:]
            if dtype==str:
                strlist.append(entries[1:])
        if dtype==str:
            bathGrid = np.array(strlist)
    
    return bathGrid_Xs, bathGrid_Ys, bathGrid

def writeBathymetryFile(filename, grid_x, grid_y, grid_depth):
    """
    Writes bathymetry data to a file in the format expected by readBathymetryFile.

    Parameters:
        filename (str): The name of the file to write to.
        grid_x (list or np.ndarray): The X coordinates of the grid.
        grid_y (list or np.ndarray): The Y coordinates of the grid.
        grid_depth (np.ndarray): The bathymetry grid (depth values).
    """
    with open(filename, 'w') as f:
        # Write a placeholder header
        f.write("--- MoorPy Bathymetry Input File ---\n")
        
        # Write the number of grid values in the x and y directions
        f.write(f"nGridX {len(grid_x)}\n")
        f.write(f"nGridY {len(grid_y)}\n")
        
        # Write the X coordinates
        f.write(" ".join(map(str, grid_x)) + "\n")
        
        # Write the Y coordinates and the bathymetry grid
        for i, y in enumerate(grid_y):
            row = [y] + list(grid_depth[i, :])
            f.write(" ".join(map(str, row)) + "\n")
            
def getSoilTypes(filename):
    '''function to read in a preliminary input text file format of soil type information'''

    soilProps = {}

    f = open(filename, 'r')
    
    for line in f:
        if line.count('---') > 0 and (line.upper().count('SOIL TYPES') > 0):
            line = next(f) # skip this header line, plus channel names and units lines
            var_names = line.split()
            line = next(f)
            line = next(f)
            while line.count('---') == 0:
                entries = line.split()
                soilProps[entries[0]] = {}
                for iv,var in enumerate(var_names[1:]):
                    # convert entries to strings unless there is 
                    if entries[iv+1] == '-':
                        soilProps[entries[0]][var] = [0]
                    else:
                        soilProps[entries[0]][var] = [float(entries[iv+1])]
                line = next(f)
    
    f.close()

    return soilProps





def convertLatLong2Meters(zerozero, lats, longs):
    '''Convert a list of latitude and longitude coordinates into
    x-y positions relative to a project reference point.
    
    Parameters
    ----------
    zerozero : tuple
        A tuple or list of two values, x and y, of the project 
        reference point
    lats : array
        array of latitude coordinates (y positions)
    longs : array
        array of longitude coordinates (x positions)

    Returns
    -------
    Xs : array
        x values of grid points (from longitudes) [m]
    Ys : array
        y values of grid points (from latitudes) [m]
    '''
    
    import geopy.distance
    
    Xs = np.zeros(len(longs))
    Ys = np.zeros(len(lats))
    for i in range(len(longs)):
        if longs[i] < zerozero[1]:
            sign = -1
        else:
            sign = 1
        Xs[i] = geopy.distance.distance(zerozero, (zerozero[0], longs[i])).km*1000*sign
    for i in range(len(lats)):
        if lats[i] < zerozero[0]:
            sign = -1
        else:
            sign = 1
        Ys[i] = geopy.distance.distance(zerozero, (lats[i], zerozero[1])).km*1000*sign

    return Xs, Ys






def processASC(gebcofilename, lat, lon, outfilename=""):
    '''Process an ASC file of bathymetry information and convert into
    a rectangular bathymetry grid in units of m relative to the 
    project reference point.
    
    Parameters
    ----------
    filename : string
        GEBCO or similar filename ASC file..
    lat : float
        lattitude of reference point to use for array y grid
    long : float
        lattitude of reference point to use for array x grid
    outfilename : string, optional
        If provided, writes a MoorDyn/MoorPy style bathymetry file

    Returns
    -------
    Xs : array
        x values of grid points [m]
    Ys : array
        y values of grid points [m]
    depths  : 2D array
        water depth grid (positive down) [m]
    lats : array
        array of latitude coordinates (y positions)
    longs : array
        array of longitude coordinates (x positions)
    '''

    depths = -np.loadtxt(gebcofilename, skiprows=6)
    nrows = len(depths)
    ncols = len(depths[0])

    newlinedata = []
    with open(gebcofilename) as f:
        lines = f.readlines()
    for i,line in enumerate(lines):
        if i < 6: newlinedata.append(line.split())
        if i==2: xllcorner = float(line.split()[1])
        if i==3: yllcorner = float(line.split()[1])
        if i==4: cellsize = float(line.split()[1])

    longs = np.linspace(xllcorner, xllcorner+ncols*cellsize, ncols)
    lats  = np.linspace(yllcorner, yllcorner+nrows*cellsize, nrows)

    zerozero = (lat, lon)  # lattitude and longitude of reference point (grid origin)

    Xs, Ys = convertLatLong2Meters(zerozero, lats, longs)

    # assuming that we don't need to change the depth values based on the curvature of the earth
    # assuming that we don't need to adjust the x/y values based on arcseconds due to curvature
    
    # ----- save a MoorDyn/MoorPy-style bathymetry file if requested -----
    
    if len(outfilename) > 0:

        f = open(os.path.join(os.getcwd(), outfilename), 'w')
        f.write('--- MoorPy Bathymetry Input File ---\n')
        f.write(f'nGridX {ncols}\n')
        f.write(f'nGridY {nrows}\n')
        f.write(f'      ')
        for ix in range(len(Xs)):
            f.write(f'{Xs[ix]:.2f} ')
        f.write('\n')
        for iy in range(len(Ys)):
            f.write(f'{Ys[iy]:.2f} ')
            for id in range(len(depths[iy])):
                iy2 = len(depths) - iy-1
                f.write(f'{depths[iy2,id]} ')
            f.write('\n')

        f.close()

    return Xs, Ys, depths, lats, longs


def processGeotiff(filename, lat, lon, outfilename="processGeotiff.txt", **kwargs):
    '''Process a geotiff file containing bathymetry (or other info)
    and convert into a rectangular bathymetry grid in units of m relative to 
    the project reference point.
    
    Parameters
    ----------
    filename : string
        Path and name of geotiff file to load.
    lat : float
        lattitude of reference point to use for array y grid
    long : float
        lattitude of reference point to use for array x grid
    outfilename : string, optional
        If provided, writes a MoorDyn/MoorPy style bathymetry file
    kwargs : dict
        Optional extra arguments that will be relayed to convertBathymetry2Meters,
        can be used to specify desired x and y grid coordinates.

    Returns
    -------
    Xs : array
        x values of grid points [m]
    Ys : array
        y values of grid points [m]
    depths  : 2D array
        water depth grid (positive down) [m]
    '''

    import rasterio
    import rasterio.plot

    tiff = rasterio.open(filename)  # load the geotiff file
    
    #rasterio.plot.show(tiff)  # plot it to see that it works
    
    # note: a CRS is stored with the geotiff, accessible with tiff.crs
    
    # Get lattitude and longitude grid values
    #_, longs = rasterio.transform.xy(tiff.transform, range(tiff.height),0)
    #lats, _  = rasterio.transform.xy(tiff.transform, 0, range(tiff.width-1,-1,-1))
    height, width = tiff.shape
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    longs_mesh, lats_mesh = rasterio.transform.xy(tiff.transform, rows, cols)
    longs = np.array(longs_mesh)[0,:]
    lats = np.flip(np.array(lats_mesh)[:,0])
    # lats data provided from top left corner, i.e., latitudes are descending. It seems that the following interpolation functions (getDepthFromBathymetry)
    # can only work if latitudes start small and increase, meaning that the first latitude entry has to be the bottom left corner
    
    # Depth values in numpy array form
    depths = -tiff.read(1)
    depths = np.flipud(depths)
    # because the interpolation functions require the latitude array to go from small to big (i.e., the bottom left corner), we need to flip the depth matrix to align
    # it will all get sorted out later to what it should be geographically when plotting in MoorPy
    
    
    # Use Stein's methods
    from famodel.geography import getLatLongCRS, getTargetCRS, getCustomCRS, convertBathymetry2Meters, writeBathymetryFile, convertLatLong2Meters
    
    # extract the coordinate reference systems needed (pyproj CRS objects)
    latlong_crs = tiff.crs
    #target_crs = getTargetCRS(lon, lat)     # should be UTM 10N for Humboldt/California coast
    target_crs = getCustomCRS(lon, lat)     # get custom CRS centered around the lat/long point you want
    
    # get the centroid/reference location in lat/long coordinates
    centroid = (lon, lat)

    # get the centroid/reference location in target_crs coordinates
    #centroid_utm = (lon, lat)
    _, _, centroid_utm = convertLatLong2Meters([centroid[0]], [centroid[1]], centroid, latlong_crs, target_crs, return_centroid=True)
    
    # set the number of rows and columns to use in the MoorPy bathymetry file
    ncols = 100
    nrows = 100
    
    # convert bathymetry to meters
    bath_xs, bath_ys, bath_depths = convertBathymetry2Meters(longs, lats, depths, 
                                                             centroid, centroid_utm, 
                                                             latlong_crs, target_crs, 
                                                             ncols, nrows, **kwargs)
    # export to MoorPy-readable file
    writeBathymetryFile(outfilename, bath_xs, bath_ys, bath_depths)

    return bath_xs, bath_ys, bath_depths



def getCoast(Xbath, Ybath, depths):
    '''Gets the x and y coordinates of the coastline from the bathymetry
    data to be used for plotting.
        
    Parameters
    ----------
    Xbath : array
        x values of bathymetry grid points [m]
    Ybath : array
        y values of bathymetry grid points [m]
    depths  : 2D array
        water depth grid (positive down) [m]

    Returns
    -------
    xcoast : array
        x values of coastal grid points [m]
    ycoast : array
        y values of coastal grid points [m]
    '''
    
    xcoast = np.zeros(len(Ybath))
    ycoast = np.zeros(len(Ybath))
    for i in range(len(depths)):
        j = 0
        while np.sign(depths[i,j])==1:
            ixc = j
            j += 1
        #ixc = np.argmin(np.abs(depths[i]))
        iyc = len(depths) - i-1
        xcoast[i] = Xbath[ixc]
        ycoast[i] = Ybath[iyc]
    
    return xcoast, ycoast


def processBoundary(filename, lat, lon,meters=True):
    '''Reads boundary information from a CSV file and stores the boundary 
    coordinate list in a set of arrays. This function can be extended to
    deal with multiple boundary sets.
        
    Parameters
    ----------
    filename : string
        Filename containing columns of x and y coordinates of boundary.
    lat : float
        lattitude of reference point to use for array y grid
    long : float
        lattitude of reference point to use for array x grid

    Returns
    -------
    Xs : array
        x values of grid points [m]
    Ys : array
        y values of grid points [m]
    '''
    
    import pandas as pd
    
    zerozero = (lat, lon)  # lattitude and longitude of reference point (grid origin)
    
    delin = pd.read_csv(filename)
    longs = np.array(delin['X_UTM10'])
    lats = np.array(delin['Y_UTM10'])
    
    if meters:
        Xs = longs
        Ys = lats
    else:
        Xs, Ys = convertLatLong2Meters(zerozero, lats, longs)
    #breakpoint()
    return Xs, Ys


def resampleGrid(x_new, y_new, x_old, y_old, grid_values):
    '''Interpolate an existing array of values on a rectangular grid to a new
    rectangular grid.
    
    Parameters
    ----------
    x_new : list
        x values of the new grid to interpolate to
    y_new : list
        y values of the new grid to interpolate to
    x_old : list
        x values of the original grid
    y_old : list
        x values of the original grid
    grid_values : 2D array
        The values on the old grid to be interpolated from (dimensions must
        match the length of y_old and x_old, in that order).
    
    Returns
    -------
    grid_values_new : 2D array
        Interpolated grid values on y_new and x_new grid lines.
    '''
    
    grid_values_new = np.zeros([len(y_new), len(x_new)])
    
    for i in range(len(y_new)):
        for j in range(len(x_new)):
            grid_values_new[i,j], _ = getDepthFromBathymetry(x_new[j], y_new[i],
                                                   x_old, y_old, grid_values)
    
    return grid_values_new


def getInterpNums(xlist, xin, istart=0):  # should turn into function in helpers
    '''
    Paramaters
    ----------
    xlist : array
        list of x values
    xin : float
        x value to be interpolated
    istart : int
        first lower index to try
    
    Returns
    -------
    i : int
        lower index to interpolate from
    fout : float
        fraction to return   such that y* = y[i] + fout*(y[i+1]-y[i])
    '''
    
    if np.isnan(xin):
        raise Exception('xin value is NaN.')
    
    nx = len(xlist)
  
    if xin <= xlist[0]:  #  below lowest data point
        i = 0
        fout = 0.0
  
    elif xlist[-1] <= xin:  # above highest data point
        i = nx-1
        fout = 0.0
  
    else:  # within the data range
 
        # if istart is below the actual value, start with it instead of 
        # starting at 0 to save time, but make sure it doesn't overstep the array
        if xlist[min(istart,nx)] < xin:
            i1 = istart
        else:
            i1 = 0

        for i in range(i1, nx-1):
            if xlist[i+1] > xin:
                fout = (xin - xlist[i] )/( xlist[i+1] - xlist[i] )
                break
    
    return i, fout


def interpFromGrid(x, y, grid_x, grid_y, values):
    '''Interpolate from a rectangular grid of values.'''

    # get interpolation indices and fractions for the relevant grid panel
    ix0, fx = getInterpNums(grid_x, x)
    iy0, fy = getInterpNums(grid_y, y)

    # handle end case conditions
    if fx == 0:
        ix1 = ix0
    else:
        ix1 = min(ix0+1, values.shape[1])  # don't overstep bounds
    
    if fy == 0:
        iy1 = iy0
    else:
        iy1 = min(iy0+1, values.shape[0])  # don't overstep bounds
    
    # get corner points of the panel
    c00 = values[iy0, ix0]
    c01 = values[iy1, ix0]
    c10 = values[iy0, ix1]
    c11 = values[iy1, ix1]

    # get interpolated points and local value
    cx0    = c00 *(1.0-fx) + c10 *fx
    cx1    = c01 *(1.0-fx) + c11 *fx
    c0y    = c00 *(1.0-fy) + c01 *fy
    c1y    = c10 *(1.0-fy) + c11 *fy
    value  = cx0 *(1.0-fy) + cx1 *fy

    # get local slope
    dx = grid_x[ix1] - grid_x[ix0]
    dy = grid_y[iy1] - grid_y[iy0]
    
    # deal with being on an edge or a zero-width grid increment
    if dx > 0.0:
        dc_dx = (c1y-c0y)/dx
    else:
        dc_dx = c0y*0  # maybe this should raise an error
    
    if dy > 0.0:
        dc_dy = (cx1-cx0)/dy
    else:
        dc_dy = cx0*0  # maybe this should raise an error
    
    # return the interpolated value, the derivatives, and the grid indices
    return value, dc_dx, dc_dy, ix0, iy0



def getDepthFromBathymetry(x, y, grid_x, grid_y, grid_depth, index=False):
    ''' interpolates local seabed depth and normal vector
    
    Parameters
    ----------
    x, y : float
        x and y coordinates to find depth and slope at [m]
    
    Returns
    -------        
    depth : float
        local seabed depth (positive down) [m]
    nvec : array of size 3
        local seabed surface normal vector (positive out) 
    index : bool, optional
        If True, will also retun ix and iy - the indices of the intersected
        grid panel.
    '''
    
    # Call general function for 2d interpolation
    depth, dc_dx, dc_dy, ix0, iy0 = interpFromGrid(x, y, grid_x, grid_y, grid_depth)
    
    # Compute unit vector of the seabed panel
    nvec = np.array([dc_dx, dc_dy, 1.0])/np.linalg.norm([dc_dx, dc_dy, 1.0])
    
    if index:
        return depth, nvec, ix0, iy0
    else:
        return depth, nvec


def getDepthFromBathymetryMesh(x, y, bathXs_mesh, bathYs_mesh, bath_depths, tol=1e4):
    ''' interpolates local seabed depth from a non-square bathymetry mesh grid
    
    Parameters
    ----------
    x, y : float
        x and y coordinates to find depth and slope at [m]
    
    Returns
    -------        
    depth : float
        local seabed depth (positive down) [m]
    nvec : array of size 3
        local seabed surface normal vector (positive out) 
    '''
    
    import geopy.distance
    from shapely import Point, LineString, Polygon

    found = False

    # loop through the bathymetry meshes to find the polygon of the mesh where to interpolate the depths from
    for j in range(len(bathYs_mesh)-1):
        for i in range(len(bathXs_mesh[0])-1):

            if np.abs(x-bathXs_mesh[j,i]) > tol or np.abs(y-bathYs_mesh[j,i]) > tol:
                pass
            else:
                # save the point of interest in a shapely Point object
                point = Point(x, y)

                # create a polygon based on the corner points for each vertex in the bathymetry mesh
                corner1 = (bathXs_mesh[j,i],bathYs_mesh[j,i])
                corner2 = (bathXs_mesh[j+1,i],bathYs_mesh[j+1,i])
                corner3 = (bathXs_mesh[j+1,i+1],bathYs_mesh[j+1,i+1])
                corner4 = (bathXs_mesh[j,i+1],bathYs_mesh[j,i+1])
                polygon = Polygon([corner1, corner2, corner3, corner4])
                # create lines that connect between each vertex/corner - hard-coded to be a 4-sided polygon
                line1 = LineString([corner1, corner2])
                line2 = LineString([corner2, corner3])
                line3 = LineString([corner3, corner4])
                line4 = LineString([corner4, corner1])
                # if the point of interest is within the polygon or lies on the line, then set interpolation variables
                if point.within(polygon) or line1.distance(point) < 1e-8 or line2.distance(point) < 1e-8 or line3.distance(point) < 1e-8 or line4.distance(point) < 1e-8:
                    # indices to use to reference depth values if point is in the current polygon
                    ix0 = i
                    ix1 = i+1
                    iy0 = j
                    iy1 = j+1
                    # bathymetry depths at each index
                    c00 = bath_depths[iy0, ix0]
                    c01 = bath_depths[iy1, ix0]
                    c10 = bath_depths[iy0, ix1]
                    c11 = bath_depths[iy1, ix1]
                    # create lines that go between the point of interest and each corner of the polygon
                    lineC1P = LineString([corner1, point])
                    lineC2P = LineString([corner2, point])
                    lineC3P = LineString([corner3, point])
                    lineC4P = LineString([corner4, point])
                    # extrude those lines to make sure they intersect an outer line of the polygon
                    def getExtrapolatedLine(p1, p2, ratio=1000):
                        a = p1
                        b = (p1[0]+ratio*(p2[0]-p1[0]), p1[1]+ratio*(p2[1]-p1[1]) )
                        return LineString([a,b])
                    lineC1P_extrude = getExtrapolatedLine(corner1, [point.x, point.y])
                    lineC2P_extrude = getExtrapolatedLine(corner2, [point.x, point.y])
                    lineC3P_extrude = getExtrapolatedLine(corner3, [point.x, point.y])
                    lineC4P_extrude = getExtrapolatedLine(corner4, [point.x, point.y])
                    # create interpolation ratios based on how close the point of interest is to the intersection point of the line going from the corner to extrude and an opposing line of the polygon
                    def getInterpRatio(line_extruded, lineCP, line_check1, line_check2, corner):
                        if line_extruded.intersection(line_check1).is_empty and line_extruded.intersection(line_check2).is_empty:
                            fL = 0.0           # if the extruded line is empty, it means it didn't get extruded, which means the point of interest is on the corner
                        else:
                            if line_extruded.intersection(line_check1).is_empty != True:        # check to see if it crosses one of the opposing two lines of the polygon
                                fL = lineCP.length / LineString([line_extruded.intersection(line_check1), corner]).length
                            else:
                                fL = lineCP.length / LineString([line_extruded.intersection(line_check2), corner]).length
                        return fL
                    fL1 = getInterpRatio(lineC1P_extrude, lineC1P, line2, line3, corner1)
                    fL2 = getInterpRatio(lineC2P_extrude, lineC2P, line4, line3, corner2)
                    fL3 = getInterpRatio(lineC3P_extrude, lineC3P, line1, line4, corner3)
                    fL4 = getInterpRatio(lineC4P_extrude, lineC4P, line1, line2, corner4)

                    # calculate the interpolated depth based on where the point of interest lies within the plane of the polygon, using the above ratios
                    depth = c00*(1-fL1) + c01*(1-fL2) + c10*(1-fL3) + c11*(1-fL4)
                    
                    found = True
                    break
            if found:
                break
            
    return depth


def getPlotBounds(latsorlongs_boundary, zerozero, long=True):
    '''Gets the x and y bounds to be used in MoorPy.System.plot() so 
    that the center of the matplotlib plot will center around a 
    reference point for ease of viewing
        
    Parameters
    ----------
    latsorlongs_boundary : array
        An array of latitude or longitude coordinates
    zerozero : tuple
        latitude and longitude of reference point
    long : bool, optional
        flag for whether latitudes or longitudes are being used

    Returns
    -------
    xbmin : float
        x (or y) value to set minimum plotting bounds relative to 
        the project reference point [m]
    xbmax : float
        x (or y) value to set maximum plotting bounds relative to 
        the project reference point [m]
    '''
    
    import geopy.distance
        
    if long:
        il = 1
    else:
        il = 0
    
    xmed = latsorlongs_boundary[int((len(latsorlongs_boundary) + 1) / 2)]
    xmin = latsorlongs_boundary[0]
    xmax = latsorlongs_boundary[-1]
    
    newxmin = xmin + (zerozero[il]-xmed)
    newxmax = xmax + (zerozero[il]-xmed)
    
    # convert lats/longs into m relative to project reference point
    if newxmin < zerozero[il]:
        sign = -1
    else:
        sign = 1
    if long:
        xbmin = geopy.distance.distance(zerozero, (zerozero[il-1], newxmin)).km*1000*sign
    else:
        xbmin = geopy.distance.distance(zerozero, (newxmin, zerozero[il-1])).km*1000*sign

    # convert lats/longs into m relative to project reference point
    if newxmax < zerozero[il]:
        sign = -1
    else:
        sign = 1
    if long:
        xbmax = geopy.distance.distance(zerozero, (zerozero[il-1], newxmax)).km*1000*sign
    else:
        xbmax = geopy.distance.distance(zerozero, (newxmax, zerozero[il-1])).km*1000*sign
    
    return xbmin, xbmax


if __name__ == '__main__':
    
    centroid = (40.928, -124.708)  #humboldt    
    xs = np.arange(-30000,30001,400)
    ys = np.arange(-40000,40001,400)
    
    xs, ys, depths = processGeotiff('humboldt.tif', centroid[0], centroid[1], xs=xs, ys=ys, outfilename='test output.txt')
    
    import moorpy as mp
    ms = mp.System(depth=np.max(depths), bathymetry='test output.txt')
    ms.initialize()
    ms.plot(hidebox=True, args_bath={'cmap':'viridis'})
    '''
    # try converting to a different grid
    x_new = np.arange(-20000, 20001, 800)
    y_new = np.arange(-20000, 20001, 800)
    depths_new = resampleGrid(x_new, y_new, xs, ys, depths)
    '''
    plt.show()
