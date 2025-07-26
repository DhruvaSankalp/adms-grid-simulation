
# Advanced Distribution Management System (ADMS) - Mega Simulation

This repository simulates a **real-world ADMS** with intelligent SCADA control, priority-based restoration, and fault-tolerant grid automation at scale.

---

## Key Features

### Scaled Smart Grid
- 1,000+ Load Nodes across 10 geographic zones
- 30 Substations + 150+ DER-enabled loads
- Priority-based load classification: High, Medium, Low

### Fault Simulation
- Cascading blackout across multiple zones
- Removal of DERs and substations in critical regions

### SCADA Logic
- Smart switching with retry and escalation logic
- Simulated SCADA command logs with timestamps and delays

### Cost Engine
- Outage cost by load criticality ($/minute)
- SCADA switching cost tracking
- Per-node restoration cost report

### Visualization
- Priority-based cost breakdown chart
- Logs and metrics for decision support
  

---

## How to Run

```bash
git clone https://github.com/DhruvaSankalp/swarm-manet-simulation.git
cd swarm-manet-simulation
python adms_simulation.py
```

---

## Credits

Created by Dhruva Sankalp with assistance from ChatGPT-4o  
Inspired by real-world utility grid operations and SCADA systems.

---

## License
MIT License
