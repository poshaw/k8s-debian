#!/bin/bash

# Confirm before shutting down the cluster
read -p "Are you sure you want to shut down the cluster? (y/n) " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee]?[Ss]?$ ]]; then
    echo "Aborting shutdown."
    exit 0
fi

# Prompt the user for their sudo password
echo -n "Please enter your sudo password: "
read -s SUDO_PASSWORD
echo

# Validate sudo password
if [[ -z "$SUDO_PASSWORD" ]]; then
    echo "Sudo password cannot be empty."
    exit 1
fi

worker_nodes=('kw1.lan')

# Validate worker nodes
if [[ ${#worker_nodes[@]} -eq 0 ]]; then
    echo "No worker nodes found."
    exit 1
fi

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
    if ! ssh "${node}" "echo \"$SUDO_PASSWORD\" | sudo -S shutdown -h now"; then
        echo "Failed to shutdown node ${node}"
        exit 1
    fi
done

# Wait for the worker nodes to shut down
for node in "${worker_nodes[@]}"; do
    echo "Waiting for worker node ${node} to shut down..."
    while ssh "$node" "uptime" &> /dev/null; do
        sleep 5
    done
done

# Shutdown master/control-plane node
echo "Shutting down master/control-plane node..."
if ! echo "$SUDO_PASSWORD" | sudo -S shutdown -h now; then
    echo "Failed to shutdown master/control-plane node"
    exit 1
fi
