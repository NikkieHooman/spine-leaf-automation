# Spine–Leaf Automation

This repository provides a complete Infrastructure-as-Code (IaC) pipeline for emulating a Spine–Leaf data-center fabric using Ansible and NAPALM. It enables:

* **Idempotent deployments**: Ensure consistent, repeatable configurations
* **Version-controlled network code**: All configurations templatized in Jinja2
* **Automated tests & health checks**: Connectivity verification, OSPF/BGP adjacencies, ECMP pings
* **Safe rollback capabilities**: Restore golden configs on drift or error

---

## Repository Layout

```
ansible/
├─ inventories/
│  └─ production.yml      
├─ group_vars/
│  ├─ all.yml            
│  ├─ spine.yml           
│  └─ leaf.yml            
├─ roles/
│  └─ napalm_config/
│     ├─ defaults/
│     │  └─ main.yml      
│     ├─ tasks/
│     │  ├─ push.yml       
│     │  ├─ rollback.yml   
│     │  └─ tests.yml     
│     └─ templates/
│        ├─ spine.j2      
│        ├─ leaf.j2       
│        ├─ spine_evpn.j2 
│        ├─ leaf_evpn.j2   
│        └─ netflow.j2     
└─ playbooks/
   ├─ day0_underlay.yml   
   ├─ day1_overlay.yml    
   ├─ verify_connectivity.yml 
   ├─ netflow_setup.yml   
   ├─ cleanup.yml          
   └─ run_all.sh           
```

---

## Prerequisites

* Ansible 2.12+
* NAPALM & appropriate network driver collections installed
* Python 3.8+ (for custom NAPALM modules)
* SSH access to all spine & leaf devices

---

## Usage

1. **Clone the repository**

   ```bash
   git clone https://github.com/NikkieHooman/spine-leaf-automation.git
   cd spine-leaf-automation/ansible
   ```

2. **Configure Inventory and Variables**

   * Edit `inventories/production.yml` with your device IPs
   * Update `group_vars/all.yml` with credentials
   * Adjust spine/leaf-specific variables in `group_vars/spine.yml` and `leaf.yml`

3. **Run Day 0 Underlay**

   ```bash
   ansible-playbook -i inventories/production.yml day0_underlay.yml
   ```

4. **Run Day 1 Overlay**

   ```bash
   ansible-playbook -i inventories/production.yml day1_overlay.yml
   ```

5. **Verify Connectivity**

   ```bash
   ansible-playbook -i inventories/production.yml verify_connectivity.yml
   ```

6. **Configure NetFlow/IPFIX**

   ```bash
   ansible-playbook -i inventories/production.yml netflow_setup.yml
   ```

7. **Cleanup / Rollback**

   ```bash
   ansible-playbook -i inventories/production.yml cleanup.yml
   ```

8. **Run All**

   ```bash
   ./run_all.sh
   ```
