output "cluster_nodes" {
  description = "All cluster nodes and their IPs"
  value = {
    for name, node in local.cluster_nodes :
    name => {
      hostname = node.name
      ip       = node.ip
      role     = node.role
    }
  }
}

output "grafana_url" {
  description = "Grafana dashboard URL"
  value       = "http://192.168.1.114:3000"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://192.168.1.114:9090"
}

output "api_url" {
  description = "JobPulse API URL"
  value       = "http://192.168.1.104:30500"
}
