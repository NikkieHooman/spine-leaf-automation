set -e
PLAYBOOKS=(
  day0_underlay.yml
  day1_overlay.yml
  verify_connectivity.yml
  netflow_setup.yml
)
for pb in "${PLAYBOOKS[@]}"; do
  echo "  Executing $pb"
  ansible-playbook -i inventories/production.yml "playbooks/$pb"
  echo "  $pb complete"
done

