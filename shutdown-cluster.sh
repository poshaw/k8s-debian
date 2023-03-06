#!/bin/bash

# Prompt the user for their sudo password
echo -n "Please enter your sudo password: "
read -s SUDO_PASSWORD
echo

worker_nodes=('kw1.lan')

# Cordon the node and evict the workloads
for node in "${worker_nodes[@]}"; do
    echo "Cordoning node ${node}..."
    kubectl cordon "${node}"
    echo "Draining node ${node}..."
    kubectl drain "${node}" --ignore-daemonsets --delete-local-data --force
done

# Shutdown worker nodes
for node in "${worker_nodes[@]}"; do
    echo "Shutting down node ${node}..."
    ssh ${node}  "echo "$SUDO_PASSWORD" | sudo -S shutdown -h now"
done

# Wait for the worker node to shut down
for node in "${worker_nodes[@]}"; do
    echo "Waiting for worker node to shut down..."
    while ssh $node "uptime" &> /dev/null; do
        sleep 5
    done
done

# Shutdown master/control-plane node
echo "Shutting down master/control-plane node..."
echo "$SUDO_PASSWORD" | sudo -S shutdown -h now
