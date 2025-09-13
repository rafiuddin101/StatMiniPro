#!/usr/bin/env python3
import random
import matplotlib.pyplot as plt

# Generate a simple random undirected network (Erdos-Renyi)
n_nodes = 50
p_edge = 0.05

# Initialize adjacency list
adj = {i: set() for i in range(n_nodes)}

# Add edges randomly
for i in range(n_nodes):
    for j in range(i+1, n_nodes):
        if random.random() < p_edge:
            adj[i].add(j)
            adj[j].add(i)

# Compute degree distribution
degrees = [len(adj[node]) for node in adj]

# Function to perform BFS and compute distances from a source
from collections import deque

def bfs_distances(adj, source):
    distances = {node: None for node in adj}
    distances[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if distances[v] is None:
                distances[v] = distances[u] + 1
                queue.append(v)
    return distances

# Compute distances from node 0
distances = bfs_distances(adj, 0)

# Plot degree distribution
plt.figure()
plt.hist(degrees, bins=range(max(degrees)+2), align='left')
plt.title('Degree Distribution of Random Network')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('degree_distribution.png')
print('Degree distribution plot saved as degree_distribution.png.')

# Print average degree and average distance
avg_degree = sum(degrees)/len(degrees)
avg_distance = sum(d for d in distances.values() if d is not None)/len([d for d in distances.values() if d is not None])
print(f'Average degree: {avg_degree:.2f}')
print(f'Average distance from node 0 (connected nodes): {avg_distance:.2f}')
