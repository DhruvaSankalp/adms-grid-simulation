
import networkx as nx
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Constants
TOTAL_LOADS = 1000
NUM_SUBSTATIONS = 30
DER_RATIO = 0.15
PRIORITY_DISTRIBUTION = {5: 100, 3: 300, 1: 600}
ZONES = 10

# Build large-scale ADMS graph
G_scaled = nx.Graph()

# Add substations
for i in range(1, NUM_SUBSTATIONS + 1):
    node = f"S{i}"
    zone = random.randint(1, ZONES)
    G_scaled.add_node(node, type="source", priority=5, zone=zone, DER=False)

# Add load nodes with priorities and DER
load_id = 1
for prio, count in PRIORITY_DISTRIBUTION.items():
    for _ in range(count):
        node = f"L{load_id}"
        zone = random.randint(1, ZONES)
        has_DER = random.random() < DER_RATIO
        G_scaled.add_node(node, type="load", priority=prio, zone=zone, DER=has_DER)
        load_id += 1

# Randomly connect nodes with redundancy
all_nodes = list(G_scaled.nodes)
for _ in range(TOTAL_LOADS * 2):  # ensure connectivity
    n1, n2 = random.sample(all_nodes, 2)
    if n1 != n2 and not G_scaled.has_edge(n1, n2):
        G_scaled.add_edge(n1, n2, status=1)

# Simulate cascading blackout in zones 1 and 2
fault_zones = [1, 2]
G_cascade = G_scaled.copy()
nodes_to_remove = [
    n for n, d in G_cascade.nodes(data=True)
    if d.get('zone') in fault_zones and (d['type'] == 'source' or d['DER'])
]
G_cascade.remove_nodes_from(nodes_to_remove)

# Identify disconnected nodes by priority
remaining_sources = [
    n for n, d in G_cascade.nodes(data=True)
    if d['type'] == 'source' or d['DER']
]
disconnected_by_priority = {5: [], 3: [], 1: []}
for comp in nx.connected_components(G_cascade):
    if not any(n in comp for n in remaining_sources):
        for n in comp:
            if G_cascade.nodes[n]['type'] == 'load':
                prio = G_cascade.nodes[n]['priority']
                disconnected_by_priority[prio].append(n)

# Attempt restoration from zone 3
support_zone = 3
support_nodes = [n for n, d in G_scaled.nodes(data=True)
                 if d['zone'] == support_zone and (d['type'] == 'source' or d['DER'])]
G_restored = G_cascade.copy()
restoration_candidates = disconnected_by_priority[5] + disconnected_by_priority[3] + disconnected_by_priority[1]
restored = []
tie_links = []

for load in restoration_candidates:
    if load in G_restored.nodes:
        if support_nodes:
            support = random.choice(support_nodes)
            G_restored.add_edge(load, support, status=1)
            tie_links.append((load, support))
            if any(n in nx.node_connected_component(G_restored, load) for n in support_nodes):
                restored.append(load)

# Simulate SCADA logic with retry
SCADA_SWITCH_DELAY_SEC = 2
SCADA_RETRY_LIMIT = 2
FAILURE_PROBABILITY = 0.15

scada_log = []
scada_start = datetime.strptime("08:00:00", "%H:%M:%S")

for i, (node, target) in enumerate(tie_links[:len(restored)]):
    retries = 0
    success = False
    while retries <= SCADA_RETRY_LIMIT and not success:
        if random.random() > FAILURE_PROBABILITY:
            success = True
            status = "Success"
        else:
            retries += 1
            status = f"Failed (Retry {retries})" if retries <= SCADA_RETRY_LIMIT else "Escalated to Manual"
    exec_time = scada_start + timedelta(seconds=(i + retries) * SCADA_SWITCH_DELAY_SEC)
    scada_log.append({
        "Restored Node": node,
        "Switch To": target,
        "Retries": retries,
        "Final Status": status,
        "Command Sent": scada_start.strftime("%H:%M:%S"),
        "Executed At": exec_time.strftime("%H:%M:%S"),
        "Escalated": status == "Escalated to Manual"
    })

# Compute cost
COST_OUTAGE_PER_MIN = {5: 10, 3: 5, 1: 1}
COST_PER_SWITCH = 50
cost_records = []

for entry in scada_log:
    node = entry["Restored Node"]
    prio = G_scaled.nodes[node]['priority']
    retries = entry["Retries"]
    exec_time = datetime.strptime(entry["Executed At"], "%H:%M:%S")
    start_time = datetime.strptime(entry["Command Sent"], "%H:%M:%S")
    outage_duration_min = max(1, int((exec_time - start_time).total_seconds() / 60))
    outage_cost = outage_duration_min * COST_OUTAGE_PER_MIN[prio]
    switch_cost = (1 + retries) * COST_PER_SWITCH
    total_cost = outage_cost + switch_cost
    cost_records.append({
        "Restored Node": node,
        "Priority": prio,
        "Outage Duration (min)": outage_duration_min,
        "Outage Cost ($)": outage_cost,
        "SCADA Switches": 1 + retries,
        "Switch Cost ($)": switch_cost,
        "Total Restoration Cost ($)": total_cost
    })

cost_df = pd.DataFrame(cost_records)

# Visualize total restoration cost by priority
priority_costs = cost_df.groupby("Priority")["Total Restoration Cost ($)"].sum().reset_index()
priority_costs["Priority Label"] = priority_costs["Priority"].map({5: "High", 3: "Medium", 1: "Low"})

plt.figure(figsize=(8, 5))
plt.bar(priority_costs["Priority Label"], priority_costs["Total Restoration Cost ($)"])
plt.title("Total Restoration Cost by Load Priority")
plt.xlabel("Priority Level")
plt.ylabel("Total Cost ($)")
plt.grid(True)
plt.tight_layout()
plt.savefig("cost_by_priority.png")
