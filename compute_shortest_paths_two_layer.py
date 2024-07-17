import pandas as pd
import os
import math
import numpy as np
import networkx as nx
import my_nx as my_nx
import matplotlib.pyplot as plt
from datetime import datetime,time, timedelta
import pickle
from process_transfers import get_merged_stops, get_merged_stops_names
from heapq import heappop, heappush
import geopandas as gpd

def compute_shortest_path(G, source, target, transfer_time=6, stop_time=1):
    def dijkstra_with_transfers(G, source, target):
        
        # initilize the distance/travel time of every stop from the source stop to inifinity
        distances = {node: float('inf') for node in G.nodes()}
        distances[source] = 0
        
        
        pq = [(0, source, None)]  # (distance, current_node, current_edge_routes)
        
        # keep track of the previous stop of the shortest path
        previous_nodes = {node: None for node in G.nodes()}
        
        while pq:
            # print(pq)
            current_distance, current_node, current_edge_routes = heappop(pq)
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in G.neighbors(current_node):
                
                # if the edge is a tranfer edge between two layers, the travel time is the walking time
                # from one station to the other station
                weight = G[current_node][neighbor]['travel_time']
                edge_routes = set(G[current_node][neighbor]['routes'])
                
                # use to see if a transfer is needed
                if current_edge_routes and not current_edge_routes.intersection(edge_routes):
                    random_noise = np.random.uniform(0, 5)
                    weight += transfer_time  # Add transfer time if no common routes
                    weight += random_noise

                new_distance = current_distance + weight + stop_time
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heappush(pq, (new_distance, neighbor, edge_routes))
        
        path = []
        current_node = target
        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        path.reverse()
        
        return path, distances[target]

    shortest_path, total_travel_time = dijkstra_with_transfers(G, source, target)
    
    return shortest_path, total_travel_time