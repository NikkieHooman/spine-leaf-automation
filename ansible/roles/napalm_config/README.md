# napalm_config Role

Provides the core tasks for device configuration via NAPALM:

- **defaults/main.yml**: Global timeouts and diff tolerance  
- **tasks/**  
  - `push.yml` — Render, stage, commit, and diff configs  
  - `rollback.yml` — Revert to golden config if needed  
  - `tests.yml` — LLDP/OSPF adjacency and ECMP ping health checks  
- **templates/**: Jinja2 templates for OSPF underlay, EVPN overlay, and NetFlow  


