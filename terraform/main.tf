terraform {
  required_version = ">= 1.0"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

locals {
  cluster_nodes = {
    master = {
      name = "jobpulse-k8s-master"
      ip   = "192.168.1.104"
      role = "k8s_master"
    }
    worker = {
      name = "jobpulse-k8s-worker"
      ip   = "192.168.1.113"
      role = "k8s_worker"
    }
    monitoring = {
      name = "jobpulse-monitoring"
      ip   = "192.168.1.114"
      role = "monitoring"
    }
    cicd = {
      name = "jobpulse-cicd"
      ip   = "192.168.1.115"
      role = "cicd"
    }
  }
}

resource "null_resource" "node_connectivity_check" {
  for_each = local.cluster_nodes

  triggers = {
    node_ip = each.value.ip
  }

  provisioner "local-exec" {
    command = "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 agzo@${each.value.ip} 'echo Node ${each.value.name} is reachable'"
  }
}

resource "null_resource" "ansible_base_setup" {
  depends_on = [null_resource.node_connectivity_check]

  triggers = {
    playbook_hash  = filemd5("${path.module}/../ansible/base-setup.yml")
    inventory_hash = filemd5("${path.module}/../ansible/inventory.ini")
  }

  provisioner "local-exec" {
    command = "ansible-playbook -i ${path.module}/../ansible/inventory.ini ${path.module}/../ansible/base-setup.yml"
  }
}

resource "local_file" "cluster_info" {
  content  = templatefile("${path.module}/templates/cluster-info.tpl", {
    nodes = local.cluster_nodes
  })
  filename = "${path.module}/outputs/cluster-info.txt"
}
