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

# Confirm that each worker node is up or remove it from the worker_nodes list
for (( i=0; i<${#worker_nodes[@]}; i++ )); do
    node="${worker_nodes[$i]}"
    echo "Confirming that node ${node} is up..."
    if ! ssh "${node}" "uptime"; then
        echo "Node ${node} is not up, removing it from the worker_nodes list..."
        unset worker_nodes[$i]
    fi
done

# Validate worker nodes
if [[ ${#worker_nodes[@]} -eq 0 ]]; then
    echo "No worker nodes found."
else
	# Cordon the node and evict the workloads
	for node in "${worker_nodes[@]}"; do
		 echo "Cordoning node ${node}..."
		 kubectl cordon "${node}"
		 echo "Draining node ${node}..."
		 kubectl drain "${node}" --ignore-daemonsets --delete-emptydir-data --force
	done

	# Shutdown worker nodes
	for node in "${worker_nodes[@]}"; do
		 echo "Shutting down node ${node}..."
		 if ! ssh -o ConnectTimeout=5 "${node}" "echo \"$SUDO_PASSWORD\" | sudo -S nohup shutdown -h now >/dev/null 2>&1 &"; then
			  echo "Failed to shutdown node ${node}"
			  exit 1
		 fi
	done

	# Wait for the worker nodes to shut down
	for node in "${worker_nodes[@]}"; do
	    echo "Waiting for worker node ${node} to shut down..."
	    while ping -c1 "${node}" &> /dev/null; do
		sleep 2
	    done
	done
fi

# Shutdown master/control-plane node
echo "Shutting down master/control-plane node..."
if ! echo "$SUDO_PASSWORD" | sudo -S shutdown -h now; then
    echo "Failed to shutdown master/control-plane node"
    exit 1
fi
