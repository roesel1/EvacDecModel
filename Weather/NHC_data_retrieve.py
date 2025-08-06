"""
This script retrieves and processes hurricane data from the National Hurricane Center (NHC).
It downloads various types of hurricane-related data (storm surge, forecast, best track, wind speed)
and converts them into shapefile formats for further analysis.
"""

# Import required libraries
import os
from pathlib import Path
import geopandas
import pandas as pd
import shapely
from bs4 import BeautifulSoup
import urllib.request
import zipfile
import datetime

from statsmodels.distributions.edgeworth import cumulant_from_moments

os.environ["CPL_ZIP_ENCODING"] = "UTF-8"
from shapely.geometry import Point




def make_polygon_longitudes_negative(geometry):
    """
    Converts positive longitudes to negative in a polygon geometry.
    
    Args:
        geometry: A shapely Polygon object
        
    Returns:
        Polygon: A new polygon with modified longitude coordinates
    """
    # For polygons, modify each point in the exterior
    new_exterior_coords = [(-abs(x), y) if x > 0 else (x, y) for x, y in geometry.exterior.coords]
    return Polygon(new_exterior_coords)

# Apply the function to each geometry in the GeoDataFrame


def load_data(code="al09", year="2017", data="psurge_results"):
    """
    Downloads and processes hurricane data from NHC website.
    
    Args:
        code (str): Hurricane identifier code (default: "al09")
        year (str): Year of the hurricane (default: "2017")
        data (str): Type of data to retrieve (default: "psurge_results")
                   Options: psurge_results, forecast_results, besttrack_results, wsp
    
    Returns:
        None: Saves processed data to shapefiles
    """
    # Initialize file path and URL parameters
    fname = Path(f"../temp.zip")
    parser = 'html.parser'
    c = 0
    url = f"https://www.nhc.noaa.gov/gis/archive_{data}.php?id={code}&year={year}"
    print(url)
    print("11")

    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

    # Initialize lists to store different types of data
    empty_list = []  # For storm surge data
    day_pgn = []  # For forecast polygons
    day_lin = []  # For forecast lines
    day_pts = []  # For forecast points
    ww_wwlin = []  # For watch/warning lines
    lin = []  # For best track lines
    radii = []  # For radii data
    pts = []  # For best track points
    wind = []  # For wind data
    knt34 = []  # For 34 knot wind speed data
    knt50 = []  # For 50 knot wind speed data
    knt64 = []  # For 64 knot wind speed data

    # Flag to control download attempts
    a = False
    # Find all links in the HTML content
    links = soup.find_all('a', href=True)
    # Get total number of links for progress calculation
    number_links = len(links)
    # Iterate through each link to find and process hurricane data files
    for link in links:
        # Check if the link points to a ZIP file
        if link['href'][-4:] == ".zip":
            # Calculate and display download progress percentage
            print(c / number_links * 100)
            c += 1
            # Begin download and processing of the ZIP file
            a = True

            while a:
                local_filename, headers = urllib.request.urlretrieve("https://www.nhc.noaa.gov/gis/" + link['href'],fname)

                zip1 = zipfile.ZipFile(local_filename)
                # print(link['href'])
                shp_file = [file for file in zip1.namelist() if file.endswith('.shp')]
                # print(zip.namelist())
                # print(shp_file)

                # Process storm surge data
                if data == "psurge_results":
                    try:
                        # Read and dissolve shapefile data
                        gdf = geopandas.read_file(f"zip://{fname}/{shp_file[0]}").dissolve()
                        # Extract and format date from filename
                        gdf["date"] = datetime.datetime.strptime(link['href'].split('_')[-1].split('.')[0],
                                                                 "%Y%m%d%H").strftime("%Y-%m-%d %H:%M:%S")
                        # Extract data type from filename
                        gdf["type"] = link['href'].split('_')[-2].split('.')[0]
                        a = False
                    except:
                        print("another round")
                    empty_list.append(gdf)
                # Process forecast data files
                elif data == "forecast_results":
                    if "A" not in link['href']:
                        for shape in shp_file:
                            # Process 5-day forecast polygon data
                            if "5day_pgn" in shape:
                                # print(shape)
                                day_pgn.append(geopandas.read_file(f"zip://{fname}/{shape}", ignore_index=True))
                                a = False
                            # Process 5-day forecast line data
                            elif "5day_lin" in shape:
                                day_lin.append(geopandas.read_file(f"zip://{fname}/{shape}", ignore_index=True))
                                a = False
                            # Process 5-day forecast point data
                            elif "5day_pts" in shape:
                                day_pts.append(geopandas.read_file(f"zip://{fname}/{shape}", ignore_index=True))
                                a = False
                            # Process watch/warning line data
                            elif  "ww_wwlin"in shape:
                                        ww_wwlin.append(geopandas.read_file(f"zip://{fname}/{shape}", ignore_index=True))
                                        a = False
                                    else:
                                        print("AAAAAAAAAAA")
                    else: 
                        a = False
                # Process best track data files
                elif data == "besttrack_results":
                    for shape in shp_file:
                        # Process best track point data
                        if "pts" in shape:
                            # print(shape)
                            pts.append(
                                geopandas.read_file(f"zip://{fname}/{shape}"))
                            a = False
                        # Process best track line data
                        elif "lin" in shape:
                            lin.append(
                                geopandas.read_file(f"zip://{fname}/{shape}"))
                            a = False
                            # elif "radii" in shape:
                            #     radii.append(
                            #         geopandas.read_file(f"zip://{fname}/{shape}"))
                            a = False
                        # Process wind data
                        elif "wind" in shape:
                            wind.append(
                                geopandas.read_file(f"zip://{fname}/{shape}", ignore_index=True))
                            a = False
                        else:
                            print("AAAAAAAAAAA")
                # Process wind speed probability data
                elif data == "wsp":
                    # Extract and format date from filename
                    date = datetime.datetime.strptime(str(link['href']).split("/")[-1][:10],
                                                      "%Y%m%d%H").strftime("%Y-%m-%d %H:%M:%S")
                    print(str(link['href']).split("/")[-1][4:6])
                    print("1")
                    # Process data only for specific month (09)
                    if str(link['href']).split("/")[-1][4:6] in ["09"]:
                        print(link['href'])
                        for shape in shp_file:
                            # Process half-degree resolution data
                            if "halfDeg" in shape:
                                # Process 34 knot wind speed data 
                                # Process 34 knot wind speed data
                                if "34knt" in shape:
                                    # Read shapefile and set coordinate reference system
                                    gdf = geopandas.read_file(f"zip://{fname}/{shape}").set_crs(crs=None,
                                                                                                allow_override=True)
                                    # Extract longitude and latitude coordinates
                                    longitudes = gdf.geometry.x
                                    latitudes = gdf.geometry.y
                                    # Define longitude remapping function
                                    map_function = lambda lon: lon  # - 180
                                    # Apply remapping to longitudes
                                    remapped_longitudes = longitudes.map(map_function)
                                    # Create new point geometries with remapped coordinates
                                    gdf['geometry'] = [Point(lon, lat) for lon, lat in zip(remapped_longitudes, latitudes)]
                                    gdf["date"] =date
                                    knt34.append(gdf)
                                    a = False
                                # Process 50 knot wind speed data
                                elif "50knt" in shape:
                                    # Read shapefile and set coordinate reference system
                                    gdf = geopandas.read_file(f"zip://{fname}/{shape}").set_crs(crs=None,
                                                                                                allow_override=True)
                                    # Extract longitude and latitude coordinates
                                    longitudes = gdf.geometry.x
                                    latitudes = gdf.geometry.y
                                    # Define longitude remapping function
                                    map_function = lambda lon: lon  # - 180
                                    # Apply remapping to longitudes
                                    remapped_longitudes = longitudes.map(map_function)
                                    # Create new point geometries with remapped coordinates
                                    gdf['geometry'] = [Point(lon, lat) for lon, lat in zip(remapped_longitudes, latitudes)]
                                    gdf["date"] = date
                                    knt50.append(gdf)
                                    a = False
                                # Process 64 knot wind speed data
                                elif "64knt" in shape:
                                    # Read shapefile and set coordinate reference system
                                    gdf = geopandas.read_file(f"zip://{fname}/{shape}").set_crs(crs=None,
                                                                                                allow_override=True)
                                    # Extract longitude and latitude coordinates
                                    longitudes = gdf.geometry.x
                                    latitudes = gdf.geometry.y
                                    # Define longitude remapping function
                                    map_function = lambda lon: lon  # - 180
                                    # Apply remapping to longitudes
                                    remapped_longitudes = longitudes.map(map_function)
                                    # Create new point geometries with remapped coordinates
                                    gdf['geometry'] = [Point(lon, lat) for lon, lat in zip(remapped_longitudes, latitudes)]
                                    gdf["date"] =date
                                    # gdf['data'] =
                                    # print(fname)
                                    knt64.append(gdf)
                                    a = False
                                else:
                                    # Skip processing if shape doesn't match any wind speed category (34knt, 50knt, 64knt)
                                    print("AAAAAAAAAAA")
                                    # Commented out alternative processing method:
                                    # gdf = pd.concat([geopandas.read_file(f"zip://{fname}/{shape}") for shape in shp_file], ignore_index=True)
                                    # break
                                    # print(gdf.geometry.iloc[0].geom_type)
                                    else:
                                # Exit processing loop if not using half-degree resolution data
                                a = False
                    else:
                        a = False
        # elif link['href'][-4:] == ".kml":
        #     if data == "wsurge_results":
                # print("https://www.nhc.noaa.gov/gis/" + link['href'],
                #       fname)
                # local_filename, headers = urllib.request.urlretrieve("https://www.nhc.noaa.gov/gis/" + link['href'],
                #                                                      fname)
                # with urllib.request.urlopen('http://www.example.com/') as f:
                #     html = f.read().decode('utf-8')
                from io import BytesIO

        # Process and save storm surge probability data
        if data == "psurge_results":
            result = pd.concat(empty_list, ignore_index=True)
            result.to_file('psurge_results.shp')
        # Process and save forecast track data (polygons, lines, points, and watch/warning)
        elif data == "forecast_results":
            pd.concat(day_pgn, ignore_index=True).to_file('day_pgn_results.shp')
            pd.concat(day_lin, ignore_index=True).to_file('day_lin_results.shp')
            pd.concat(day_pts, ignore_index=True).to_file('day_pts_results.shp')
            pd.concat(ww_wwlin, ignore_index=True).to_file('ww_wwlin_results.shp')
        # Process and save best track data (points, lines, and wind fields)
        elif data == "besttrack_results":
            pd.concat(pts, ignore_index=True).to_file('besttrack_results_pts.shp')
            pd.concat(lin, ignore_index=True).to_file('besttrack_results_lin.shp')
            # pd.concat(radii, ignore_index=True).to_file('besttrack_results_radii.shp')
            pd.concat(wind, ignore_index=True).to_file('besttrack_results_wind.shp')
        # Process and save wind speed probability data for different thresholds
        elif data == "wsp":
            pd.concat(knt34, ignore_index=True).to_file('wsp_knt34.shp')  # 34 knot wind speed probability
            pd.concat(knt50, ignore_index=True).to_file('wsp_knt50.shp')  # 50 knot wind speed probability
            pd.concat(knt64, ignore_index=True).to_file('wsp_knt64.shp')  # 64 knot wind speed probability

    load_data(code="al11",data="wsurge_results")
