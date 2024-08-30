#!/bin/bash

echo "Starting apache2 service"
service apache2 start

json_body="{\"password\":\"${NEO4J_PASSWORD}\"}"

# Needs to be here for the start delay of the neo4j db in CRUSOE Observe
sleep 20
echo "neo4j available"

python3 /tmp/neo4j_update.py

if [ $? -eq 0 ]; then
    echo "PAO was updated to neo4j successfully."
else
    echo "Failed to update PAO in neo4j."
fi

exec tail -f /dev/null