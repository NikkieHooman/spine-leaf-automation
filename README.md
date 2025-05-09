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
│  └─ production.yml        # Defines spine & leaf hosts
├─ group_vars/
│  ├─ all.yml              # Shared credentials & NAPALM settings
│  ├─ spine.yml            # Spine-specific loopback & OSPF vars
│  └─ leaf.yml             # Leaf-specific VTEP, VNI, NetFlow vars
├─ roles/
│  └─ napalm_config/
│     ├─ defaults/
│     │  └─ main.yml       # Global role defaults (timeouts, diff tolerances)
│     ├─ tasks/
│     │  ├─ push.yml       # Load, commit, diff configurations
│     │  ├─ rollback.yml   # Revert to last golden config
│     │  └─ tests.yml      # LLDP/OSPF adjacency & ping tests
│     └─ templates/
│        ├─ spine.j2       # Jinja2 underlay template for spines
│        ├─ leaf.j2        # Jinja2 underlay template for leaves
│        ├─ spine_evpn.j2  # Jinja2 EVPN overlay template for spines
│        ├─ leaf_evpn.j2   # Jinja2 EVPN overlay template for leaves
│        └─ netflow.j2     # Jinja2 NetFlow/IPFIX export template
└─ playbooks/
   ├─ day0_underlay.yml    # Deploy OSPF underlay
   ├─ day1_overlay.yml     # Deploy VXLAN/EVPN overlay
   ├─ verify_connectivity.yml # Health-check playbook
   ├─ netflow_setup.yml    # Configure NetFlow/IPFIX export
   ├─ cleanup.yml          # Rollback unintended changes
   └─ run_all.sh           # Convenience script to run all playbooks
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
