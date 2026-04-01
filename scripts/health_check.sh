#!/bin/bash
HOSTS=('192.168.1.104' '192.168.1.113' '192.168.1.114' '192.168.1.115')
NAMES=('master' 'worker' 'monitoring' 'cicd')
for i in "${!HOSTS[@]}"; do
  echo "=== ${NAMES[$i]} (${HOSTS[$i]}) ==="
  ssh agzo@${HOSTS[$i]} 'echo "CPU load: $(cat /proc/loadavg | cut -d" " -f1)"; \
    echo "MEM: $(free -h | awk "/^Mem/{print \$3\"/\"\$2}")"; \
    echo "DISK: $(df -h / | awk "NR==2{print \$5}")"; \
    echo "UPTIME: $(uptime -p)"'
  echo ""
done
