#!/bin/bash
# JobPulse Cluster Status Reporter
# Shows health of all platform components in one view

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}=====================================${RESET}"
echo -e "${BOLD}  JobPulse Platform Status Report${RESET}"
echo -e "${BOLD}=====================================${RESET}"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

echo -e "${BOLD}CLUSTER NODES${RESET}"
echo "-------------------------------------"
HOSTS=('192.168.1.104' '192.168.1.113' '192.168.1.114' '192.168.1.115')
NAMES=('k8s-master' 'k8s-worker' 'monitoring' 'cicd')
for i in "${!HOSTS[@]}"; do
    RESULT=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no \
        agzo@${HOSTS[$i]} \
        'echo "cpu=$(cat /proc/loadavg | cut -d" " -f1) mem=$(free -h | awk "/^Mem/{print \$3\"/\"\$2}") disk=$(df -h / | awk "NR==2{print \$5}")"' \
        2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}UP${RESET}   ${NAMES[$i]} (${HOSTS[$i]}) | $RESULT"
    else
        echo -e "  ${RED}DOWN${RESET} ${NAMES[$i]} (${HOSTS[$i]})"
    fi
done

echo ""
echo -e "${BOLD}KUBERNETES PODS${RESET}"
echo "-------------------------------------"
ssh -o StrictHostKeyChecking=no agzo@192.168.1.104 \
    'kubectl get pods -n jobpulse --no-headers 2>/dev/null' | \
while read line; do
    if echo "$line" | grep -q "Running"; then
        echo -e "  ${GREEN}OK${RESET}   $line"
    else
        echo -e "  ${RED}ERR${RESET}  $line"
    fi
done

echo ""
echo -e "${BOLD}SERVICES${RESET}"
echo "-------------------------------------"
check_service() {
    local name=$1
    local url=$2
    local expected=$3
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" 2>/dev/null)
    if [ "$HTTP" = "$expected" ]; then
        echo -e "  ${GREEN}UP${RESET}   $name ($url) HTTP $HTTP"
    else
        echo -e "  ${RED}DOWN${RESET} $name ($url) HTTP $HTTP"
    fi
}

check_service "JobPulse API" "http://192.168.1.104:30500/health" "200"
check_service "Prometheus" "http://192.168.1.114:9090/-/healthy" "200"
check_service "Grafana" "http://192.168.1.114:3000/api/health" "200"
check_service "Alertmanager" "http://192.168.1.114:9093/-/healthy" "200"
check_service "Loki" "http://192.168.1.114:3100/ready" "200"

echo ""
echo -e "${BOLD}NODE EXPORTERS${RESET}"
echo "-------------------------------------"
for i in "${!HOSTS[@]}"; do
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 \
        "http://${HOSTS[$i]}:9100/metrics" 2>/dev/null)
    if [ "$HTTP" = "200" ]; then
        echo -e "  ${GREEN}UP${RESET}   ${NAMES[$i]} node-exporter"
    else
        echo -e "  ${RED}DOWN${RESET} ${NAMES[$i]} node-exporter"
    fi
done

echo ""
echo -e "${BOLD}=====================================${RESET}"
echo ""
