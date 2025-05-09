# Playbooks

Orchestrates each stage of deployment:

- `day0_underlay.yml` — Configure OSPF underlay  
- `day1_overlay.yml` — Configure VXLAN/EVPN overlay  
- `verify_connectivity.yml` — Run adjacency and ping tests  
- `netflow_setup.yml` — Enable NetFlow/IPFIX export  
- `cleanup.yml` — Force rollback to golden configs  
- `run_all.sh` — Helper script to run all playbooks in sequence  
