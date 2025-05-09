# Spine‑Leaf Automation

This directory contains all Ansible playbooks, roles, and variable files to automate a GNS3‑based Spine–Leaf fabric lab using NAPALM.

- **inventories/**: Host definitions (`production.yml`)  
- **group_vars/**: Shared and per‑group variables  
- **roles/napalm_config/**: Tasks, defaults, and templates for config push, diff, rollback, and tests  
- **playbooks/**: Stage‑specific playbooks and a helper script (`run_all.sh`)  

