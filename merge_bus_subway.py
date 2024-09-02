import pandas as pd
import os
import math
import numpy as np
import networkx as nx
from haversine import haversine, Unit


def merge_subway_bus(subway_network, bus_network, transfer_distance_threshold, walking_speed=1.47):
    # create a new directed graph to represent the merged network
    G_merged = nx.DiGraph()

    # Add nodes and edges from the subway network
    for node, data in subway_network.nodes(data=True):
        G_merged.add_node(f"subway_{node}", **data)
    for u, v, data in subway_network.edges(data=True):
        G_merged.add_edge(f"subway_{u}", f"subway_{v}", **data)

    # Add nodes and edges from the bus network
    for node, data in bus_network.nodes(data=True):
        G_merged.add_node(f"bus_{node}", **data)
    for u, v, data in bus_network.edges(data=True):
        G_merged.add_edge(f"bus_{u}", f"bus_{v}", **data)
        

    # transfer_distance_threshold = 0.3  # 0.5 kilometers
    for bus_node, bus_data in bus_network.nodes(data=True):
        for subway_node, subway_data in subway_network.nodes(data=True):
            bus_coords = (bus_data['pos'][0], bus_data['pos'][1])
            subway_coords = (subway_data['pos'][0], subway_data['pos'][1])
            # print(bus_coords)
            # print(subway_coords)
            distance = haversine(bus_coords, subway_coords, unit=Unit.KILOMETERS)
            if distance <= transfer_distance_threshold:
                bus_id = f"bus_{bus_node}"
                subway_id = f"subway_{subway_node}"
                # print(bus_id)
                if G_merged.has_node(bus_id) and G_merged.has_node(subway_id):
                    transfer_time = distance * 1000 / walking_speed / 60
                    G_merged.add_edge(bus_id, subway_id, layer='transfer', travel_time=transfer_time, routes=[f'transfer {bus_id} to {subway_id}'])
                    G_merged.add_edge(subway_id, bus_id, layer='transfer', travel_time=transfer_time, routes=[f'transfer {subway_id} to {bus_id}'])
                    

    return G_merged