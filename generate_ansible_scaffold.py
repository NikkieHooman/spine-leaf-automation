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
- name: Render & commit configuration via NAPALM
  napalm.napalm.napalm_install_config:
    hostname: "{{ inventory_hostname }}"
    username: "{{ ansible_user }}"
    password: "{{ ansible_password }}"
    dev_os: "{{ napalm_driver }}"
    optional_args: "{{ napalm_args }}"
    config: "{{ lookup('template', config_template) }}"
    commit_changes: true
    get_diffs: true
  register: napalm_diff

- name: Show the NAPALM diff
  debug:
    var: napalm_diff.diff
''',

    
    'ansible/roles/napalm_config/tasks/rollback.yml': '''
- name: Roll back to golden config via NAPALM
  napalm.napalm.napalm_install_config:
    hostname: "{{ inventory_hostname }}"
    username: "{{ ansible_user }}"
    password: "{{ ansible_password }}"
    dev_os: "{{ napalm_driver }}"
    optional_args: "{{ napalm_args }}"
    config_file: "ansible/roles/napalm_config/golden_configs/{{ inventory_hostname }}.cfg"
    replace_config: true
    commit_changes: true
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


    'ansible/playbooks/generate_configs.yml': '''
- name: Render Underlay & Overlay configs locally
  hosts: spine:leaf
  connection: local
  gather_facts: no

  vars:
    underlay_template: >-
      {{ 'ansible/roles/napalm_config/templates/spine.j2'
         if inventory_hostname in groups['spine']
         else 'ansible/roles/napalm_config/templates/leaf.j2' }}
    overlay_template: >-
      {{ 'ansible/roles/napalm_config/templates/spine_evpn.j2'
         if inventory_hostname in groups['spine']
         else 'ansible/roles/napalm_config/templates/leaf_evpn.j2' }}

  tasks:
    - name: Render Underlay config
      template:
        src: "{{ underlay_template }}"
        dest: "build/{{ inventory_hostname }}_underlay.cfg"

    - name: Render Overlay config
      template:
        src: "{{ overlay_template }}"
        dest: "build/{{ inventory_hostname }}_overlay.cfg"
''',
    'ansible/playbooks/day0_underlay.yml': '''
- name: Day0 Underlay Deployment
  hosts: spine:leaf
  gather_facts: no
  collections:
    - napalm.napalm
  roles:
    - role: napalm_config
      vars:
        config_template: "{{ 'spine.j2' if inventory_hostname in groups['spine'] else 'leaf.j2' }}"
''',

    'ansible/playbooks/day1_overlay.yml': '''
- name: Day1 VXLAN/EVPN Overlay
  hosts: spine:leaf
  gather_facts: no
  collections:
    - napalm.napalm
  roles:
    - role: napalm_config
      vars:
        config_template: "{{ 'spine_evpn.j2' if inventory_hostname in groups['spine'] else 'leaf_evpn.j2' }}"
''',

    'ansible/playbooks/verify_connectivity.yml': '''
- name: Verify OSPF Adjacency and ECMP
  hosts: leaf
  gather_facts: no
  connection: network_cli
  collections:
    - ansible.netcommon
    - napalm.napalm

  tasks:
    - name: Show OSPF neighbors
      ansible.netcommon.cli_command:
        command: show ip ospf neighbor
      register: ospf_data

    - name: Fail if adjacency not FULL
      ansible.builtin.fail:
        msg: "OSPF adjacency not FULL on {{ inventory_hostname }}"
      when: "'Full' not in ospf_data.stdout[0]"

    - name: Ping leaf loopbacks for ECMP check
      napalm.napalm.napalm_ping:
        hostname: "{{ inventory_hostname }}"
        username: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        dev_os: "{{ napalm_driver }}"
        dest: "{{ item }}"
        count: 5
        timeout: 2
      loop: "{{ leaf_loopbacks }}"
      register: ping_results

    - name: Fail on packet loss
      ansible.builtin.fail:
        msg: "Ping loss detected on {{ inventory_hostname }}"
      when: ping_results.results | selectattr('packet_loss_pct','>',0) | list | length > 0
''',

    'ansible/playbooks/netflow_setup.yml': '''
- name: Configure NetFlow/IPFIX
  hosts: leaf
  gather_facts: no
  collections:
    - napalm.napalm
  roles:
    - role: napalm_config
      vars:
        config_template: netflow.j2
''',

    'ansible/playbooks/cleanup.yml': '''
- name: Rollback Unintended Drift
  hosts: all
  gather_facts: no
  collections:
    - napalm.napalm
  roles:
    - role: napalm_config
      vars:
        force_rollback: true
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
