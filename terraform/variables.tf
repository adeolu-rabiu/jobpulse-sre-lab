variable "ssh_user" {
  description = "SSH username for all cluster nodes"
  type        = string
  default     = "agzo"
}

variable "cluster_network" {
  description = "Network CIDR for the cluster"
  type        = string
  default     = "192.168.1.0/24"
}
