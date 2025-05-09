import os

BASE = os.getcwd()
ANSIBLE_DIR = os.path.join(BASE, 'ansible')

templates = {
    
    'ansible.cfg': '''
[defaults]
inventory = ansible/inventories/production.yml
roles_path = ansible/roles
host_key_checking = False
''',

    
    'ansible/inventories/production.yml': '''
all:
  children:
    spine:
      hosts:
        spine-1:
          ansible_host: 127.0.0.1
          ansible_connection: local
        spine-2:
          ansible_host: 127.0.0.1
          ansible_connection: local
        spine-3:
          ansible_host: 127.0.0.1
          ansible_connection: local
    leaf:
      hosts:
        leaf-1:
          ansible_host: 127.0.0.1
          ansible_connection: local
        leaf-2:
          ansible_host: 127.0.0.1
          ansible_connection: local
        leaf-3:
          ansible_host: 127.0.0.1
          ansible_connection: local
        leaf-4:
          ansible_host: 127.0.0.1
          ansible_connection: local
        leaf-5:
          ansible_host: 127.0.0.1
          ansible_connection: local
''',

   
    'ansible/group_vars/all.yml': '''
ansible_user: admin
ansible_password: P@ssw0rd
napalm_driver: ios
napalm_args: {}

leaf_loopbacks:
  - 10.0.0.42
  - 10.0.0.46
  - 10.0.0.50
  - 10.0.0.54
  - 10.0.0.58
expected_neighbors:
  spine-1: 5
  spine-2: 5
  spine-3: 5
  leaf-1: 3
  leaf-2: 3
  leaf-3: 3
  leaf-4: 3
  leaf-5: 3
''',

    'ansible/group_vars/spine.yml': '''
asn: 65000
ospf_links:
  - interface: f0/0
    subnet: 10.0.0.0/30
  - interface: f1/0
    subnet: 10.0.0.4/30
  - interface: f2/0
    subnet: 10.0.0.8/30
  - interface: f3/0
    subnet: 10.0.0.12/30
  - interface: f4/0
    subnet: 10.0.0.16/30
''',

    'ansible/group_vars/leaf.yml': '''
asn: 65000
ospf_links:
  - interface: f0/0
    subnet: 10.0.0.0/30
  - interface: f1/0
    subnet: 10.0.0.4/30
  - interface: f2/0
    subnet: 10.0.0.8/30
  - interface: f3/0
    subnet: 10.0.0.12/30
  - interface: f4/0
    subnet: 10.0.0.16/30
evpn_peers:
  - 10.0.0.41
  - 10.0.0.21
  - 10.0.0.1
vni_map:
  user:   10010
  server: 10030
  dmz:    10050
  tenant: 10060
collector_ip: 192.168.100.10
''',

    
    'ansible/roles/napalm_config/tasks/main.yml': '''
---
- import_tasks: push.yml
  when: not force_rollback | default(false)

- import_tasks: rollback.yml
  when: force_rollback | default(false)
''',

    
    'ansible/roles/napalm_config/tasks/push.yml': '''
- name: Render candidate configuration
  napalm_config:
    hostname: "{{ inventory_hostname }}"
    template: "{{ config_template }}"
    template_vars: "{{ j2_vars }}"
    replace: true
    timeout: "{{ load_timeout }}"
  register: candidate

- name: Commit candidate configuration
  napalm_config:
    hostname: "{{ inventory_hostname }}"
    commit: true
    timeout: "{{ commit_timeout }}"
  when: candidate.diff is defined

- name: Display configuration diff
  debug:
    msg: "Config diff for {{ inventory_hostname }}:\\n{{ candidate.diff }}"
  when: candidate.diff is defined

- name: Roll back on excessive diffs
  include_tasks: rollback.yml
  when: candidate.diff is defined and (candidate.diff.splitlines() | length) > diff_tolerance
''',

    
    'ansible/roles/napalm_config/tasks/rollback.yml': '''
- name: Restore golden configuration
  napalm_config:
    hostname: "{{ inventory_hostname }}"
    rollback: true
  when: force_rollback or (candidate.diff.splitlines() | length) > diff_tolerance

- name: Verify running config after rollback
  napalm_get:
    hostname: "{{ inventory_hostname }}"
    get_config: running
  register: running_cfg

- name: Display post-rollback diff
  debug:
    msg: "Post-rollback diff for {{ inventory_hostname }}:\\n{{ running_cfg.diff }}"
  when: running_cfg.diff is defined
''',

    
    'ansible/roles/napalm_config/tasks/tests.yml': '''
- name: Check LLDP/OSPF adjacency
  napalm_get:
    hostname: "{{ inventory_hostname }}"
    get_lldp_neighbors: true
  register: lldp

- name: Fail if adjacency count is below expected
  fail:
    msg: "Adjacency down on {{ inventory_hostname }}"
  when: lldp.lldp_neighbors | length < expected_neighbors[inventory_hostname]

- name: Ping leaf loopbacks for ECMP test
  raw: |
    ping -c 3 {{ item }}
  loop: "{{ leaf_loopbacks }}"
  register: ping_results

- name: Fail on ping errors
  fail:
    msg: "Ping failed from {{ inventory_hostname }} to {{ item.item }}"
  loop: "{{ ping_results.results }}"
  when: item.rc != 0
''',

   
    'ansible/roles/napalm_config/templates/spine.j2': '''
hostname {{ inventory_hostname }}
interface Loopback0
  ip address {{ hostvars[inventory_hostname].ansible_host }} 255.255.255.255
router ospf 1
  router-id {{ hostvars[inventory_hostname].ansible_host }}
{% for link in ospf_links %}
network {{ link.subnet }} area 0
{% endfor %}
''',

    'ansible/roles/napalm_config/templates/leaf.j2': '''
hostname {{ inventory_hostname }}
interface Loopback0
  ip address {{ hostvars[inventory_hostname].ansible_host }} 255.255.255.255
router ospf 1
  router-id {{ hostvars[inventory_hostname].ansible_host }}
{% for link in ospf_links %}
network {{ link.subnet }} area 0
{% endfor %}
''',

    'ansible/roles/napalm_config/templates/spine_evpn.j2': '''
router bgp {{ asn }}
  router-id {{ hostvars[inventory_hostname].ansible_host }}
  address-family l2vpn evpn
{% for peer in evpn_peers %}
  neighbor {{ peer }} remote-as {{ asn }}
  neighbor {{ peer }} activate
{% endfor %}
''',

    'ansible/roles/napalm_config/templates/leaf_evpn.j2': '''
router bgp {{ asn }}
  router-id {{ hostvars[inventory_hostname].ansible_host }}
  address-family l2vpn evpn
{% for peer in evpn_peers %}
  neighbor {{ peer }} remote-as {{ asn }}
  neighbor {{ peer }} activate
{% endfor %}
{% for vni in vni_map.values() %}
  vni {{ vni }} l2 underlay-interface Loopback0
{% endfor %}
''',

    'ansible/roles/napalm_config/templates/netflow.j2': '''
flow exporter EXPORTER-1
  destination {{ collector_ip }}
  transport udp 2055
!
flow monitor MONITOR-1
  exporter EXPORTER-1
  record ipv4
!
interface f3/0
  ip flow monitor MONITOR-1 input
''',

    
    'ansible/playbooks/day0_underlay.yml': '''
- name: Day0 Underlay Deployment
  hosts: spine:leaf
  gather_facts: no
  roles:
    - role: napalm_config
      vars:
        config_template: "{{ 'spine.j2' if inventory_hostname in groups['spine'] else 'leaf.j2' }}"
        j2_vars:
          hostname: "{{ inventory_hostname }}"
          loopback0: "{{ hostvars[inventory_hostname].loopback0 }}"
          ospf_links: "{{ ospf\_links }}"
''',

    'ansible/playbooks/day1_overlay.yml': '''
- name: Day1 VXLAN/EVPN Overlay
  hosts: spine:leaf
  gather_facts: no
  roles:
    - role: napalm_config
      vars:
        config_template: "{{ 'spine_evpn.j2' if inventory_hostname in groups['spine'] else 'leaf_evpn.j2' }}"
        j2_vars:
          as_number: 65000
          router_id: "{{ hostvars[inventory_hostname].loopback0 }}"
          evpn_peers: "{{ evpn_peers }}"
          vni_map: "{{ vni_map }}"
''',

    'ansible/playbooks/verify_connectivity.yml': '''
- name: Verify Underlay & Overlay Connectivity
  hosts: spine:leaf
  gather_facts: no
  roles:
    - role: napalm_config
      tasks_from: tests.yml
''',

    'ansible/playbooks/netflow_setup.yml': '''
- name: Configure NetFlow/IPFIX
  hosts: leaf
  gather_facts: no
  roles:
    - role: napalm_config
      vars:
        config_template: netflow.j2
''',

    'ansible/playbooks/cleanup.yml': '''
- name: Rollback Unintended Drift
  hosts: all
  gather_facts: no
  roles:
    - role: napalm_config
      vars:
        force_rollback: true
''',

    
    'ansible/playbooks/run_all.sh': '''
#!/usr/bin/env bash
set -e
PLAYBOOKS=(
  day0_underlay.yml
  day1_overlay.yml
  verify_connectivity.yml
  netflow_setup.yml
)
for pb in "${PLAYBOOKS[@]}"; do
  echo "➡️  Executing $pb"
  ansible-playbook -i inventories/production.yml "playbooks/$pb"
  echo "  $pb complete"
done
''',
}

def main():
    for rel_path, content in templates.items():
        abs_path = os.path.join(BASE, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as f:
            f.write(content.lstrip() + '\n')
    print(f"Ansible scaffold generated at: {ANSIBLE_DIR}")

if __name__ == '__main__':
    main()
