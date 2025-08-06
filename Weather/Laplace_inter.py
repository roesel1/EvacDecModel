
import numpy as np
import  math
def circum_center(dt,triangle):
    "Calculates the center point of the circumcircle corresponding to the given triangle"

    # Retrieve coordinates of triangle points
    px_1, py_1, pz_1 = dt.get_point(triangle[0])
    px_2, py_2, pz_2 = dt.get_point(triangle[1])
    px_3, py_3, pz_3 = dt.get_point(triangle[2])
    # Area of circumcircle
    d = 2 * (px_1 * (py_2 - py_3) + px_2 * (py_3 - py_1) + px_3 * (py_1 - py_2))
    # Calculates the x,y for the circumcircle
    x = ((px_1 * px_1 + py_1 * py_1) * (py_2 - py_3) +
          (px_2 * px_2 + py_2 * py_2) * (py_3 - py_1) +
          (px_3 * px_3 + py_3 * py_3) * (py_1 - py_2)) / d

    y = ((px_1 * px_1 + py_1 * py_1) * (px_3 - px_2) +
          (px_2 * px_2 + py_2 * py_2) * (px_1 - px_3) +
          (px_3 * px_3 + py_3 * py_3) * (px_2 - px_1)) / d
    return [x, y]

def interpolate_laplace(dt, x, y):
    """
    Function that interpolates at location (x,y) in a DT with the Laplace interpolation.

    Inputs:
      dt: the startinpy DT
      x:  coordinate x to interpolate
      y:  coordinate y to interpolate

    Output:
      - the estimated value for z
      - np.nan if outside the convex hull (impossible to interpolate)
    """
    dt_vertex_v_edge_dict = {}
    # Check if point is within the convex hull
    if dt.is_inside_convex_hull((x, y)) == False:  # Check if point is in convex hull
        # print("Outside convex hull returned Nan")
        return np.nan
    # Inserts the point that will be interpolated
    new_id = dt.insert_one_pt((x, y, 0))[0]  # Zero is fake z- value

    # Gets the triangles which contain the point
    triangles_vertex = dt.incident_triangles_to_vertex(new_id)
    # Check if infinity vertex is included. Cannot calculate result for triangles including infinity triangle
    for triangle in triangles_vertex:
        if 0 in triangle:
            return np.nan

    # Loops over the triangles
    for index in range(len(triangles_vertex)):
        # Computes the circumcenter of the first triangle
        center_triangle_1 = circum_center(dt, triangles_vertex[index])
        triangle_1 = triangles_vertex[index]
        # Checks if we reached the last triangle in the list. If yes, get the first triangle in the list
        if len(triangles_vertex) == index + 1:
            # Computes the circumcenter of the second triangle
            center_triangle_2 = circum_center(dt, triangles_vertex[0])
            triangle_2 = triangles_vertex[0]
        # If last triangle in list is not reached
        else:
            # Computes the circumcenter of the second triangle
            center_triangle_2 = circum_center(dt, triangles_vertex[index + 1])
            triangle_2 = triangles_vertex[index + 1]



        # Gets the index of the point of which the voronoi edge is calculated
        dt_vertex_v_edge = (list((set(triangle_1) & set(triangle_2))))
        dt_vertex_v_edge.remove(new_id)
        # There were occurrences where dt_vertex_v_edge contained multiple indexes
        if len(dt_vertex_v_edge) != 1:
            raise Exception("Cannot determine correct dt vertex of voronoi edge")
        # Calculates length of voronoi edge
        voronoi_edge = math.sqrt(
            (center_triangle_2[0] - center_triangle_1[0]) ** 2 + (center_triangle_2[1] - center_triangle_1[1]) ** 2)
        # Calculates distance between inserted point and point of which voronoi edge is calculated
        x_pi = math.sqrt(
            (x - dt.get_point(dt_vertex_v_edge[0])[0]) ** 2 + (y - dt.get_point(dt_vertex_v_edge[0])[1]) ** 2)
        # Calculates the weight
        dt_vertex_v_edge_dict[dt_vertex_v_edge[0]] = voronoi_edge / x_pi
    # Gets the total of the weights
    total_edge_dist = sum(dt_vertex_v_edge_dict.values())


    z_value = 0
    # Calculates the contribution for the z value  of every triangle surrounding the point
    for vertex in dt_vertex_v_edge_dict.keys():
        z_value += (dt.get_point(vertex)[2] * dt_vertex_v_edge_dict[vertex]) / total_edge_dist
    # Removes the point again to get the original dt
    dt.remove(new_id)
    # print(f" Own Laplace: {z_value} Startinpy Laplace:",dt.interpolate({"method": "Laplace"}, [[x, y]]))
    return z_value


def bbox(pts_all):
    """Calculates the bounding box of the AHN point cloud"""
    pts_all_T = pts_all.T
    x_min = np.min(pts_all_T[0])
    x_max = np.max(pts_all_T[0])

    y_min = np.min(pts_all_T[1])
    y_max = np.max(pts_all_T[1])
    return (x_min, x_max, y_min, y_max)

