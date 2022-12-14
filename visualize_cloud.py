#!/usr/bin/env python3

import open3d as o3d
import numpy as np
import sys
import argparse
import os

def get_mesh_ball(downpcd):
    distances = downpcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 3 * avg_dist
    radii = np.array([radius, radius*3])
    rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        downpcd, o3d.utility.DoubleVector(radii))
    dec_mesh = rec_mesh.simplify_quadric_decimation(10000)
    dec_mesh.remove_degenerate_triangles()
    dec_mesh.remove_duplicated_triangles()
    dec_mesh.remove_duplicated_vertices()
    dec_mesh.remove_non_manifold_edges()
    return dec_mesh

def get_mesh_poisson(pcd):
    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8, width=0, scale=1.1, linear_fit=True)[0]
    bbox = pcd.get_axis_aligned_bounding_box()
    p_mesh_crop = poisson_mesh.crop(bbox)
    return p_mesh_crop


if __name__ == "__main__":
    
    # print(dir(o3d.geometry.PointCloud))
    # exit(0)
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest="input_file", nargs='?', default=os.path.join("output", "DP", "Art", "output_l9_w1_DP"))
    args, unknown = parser.parse_known_args()
    ## define parameters
    filename = args.input_file
    if isinstance(filename, list):
        filename = filename[0]
    if ".xyz" not in filename:
        filename = "" + filename + ".xyz"
    min_z = 2000

    print(f"Visualising pointclout from the file {filename}...")
    ## load points
    points = np.loadtxt(filename)

    ## filter small z-coordinate
    points = points[np.where(points[:, 2] > min_z)]

    ## create PointCloud
    cl = o3d.geometry.PointCloud()
    cl.points = o3d.utility.Vector3dVector(points)

    ## filter points noise 
    voxel_down_pcd = cl.voxel_down_sample(voxel_size=0.02)
    cl, ind = voxel_down_pcd.remove_radius_outlier(nb_points=15, radius=5) # radius filter
    #cl, ind = voxel_down_pcd.remove_statistical_outlier(nb_neighbors=50, std_ratio=.2) # statistical filter

    
    print("Compute the normal of the downsampled point cloud ...")
    downpcd = cl.voxel_down_sample(voxel_size=5)
    downpcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=40,
                                                          max_nn=50))
    o3d.io.write_point_cloud("output/3d/pointcloud.ply", downpcd, write_ascii=True, compressed=False)

    downpcd.orient_normals_towards_camera_location()
    print("Compute 3d-mesh of the downsampled point cloud ...")
    mesh = get_mesh_ball(downpcd)
    o3d.io.write_triangle_mesh("output/3d/mesh.ply", mesh, write_ascii=True, compressed=False)
    # mesh = get_mesh_poisson(downpcd)

    ## visualize results
    ## points
    o3d.visualization.draw_geometries([downpcd])
    ## normals
    o3d.visualization.draw_geometries([downpcd.voxel_down_sample(voxel_size=10)], point_show_normal=True)
    ## 3d-mesh
    o3d.visualization.draw_geometries([downpcd.voxel_down_sample(voxel_size=20), mesh])





