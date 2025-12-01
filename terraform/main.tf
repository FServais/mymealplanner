terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# SSH Key for accessing the droplet
resource "digitalocean_ssh_key" "default" {
  name       = "mealplanner-terraform-key"
  public_key = file(var.ssh_public_key_path)
}

# Firewall rules
resource "digitalocean_firewall" "web" {
  name = "mealplanner-firewall"

  droplet_ids = [digitalocean_droplet.mealplanner.id]

  # SSH
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # HTTP
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # HTTPS
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow all outbound traffic
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# The main droplet
resource "digitalocean_droplet" "mealplanner" {
  image    = "ubuntu-22-04-x64"
  name     = "mealplanner-${var.environment}"
  region   = var.region
  size     = "s-1vcpu-1gb" # Cheapest option: $6/month
  ssh_keys = [digitalocean_ssh_key.default.fingerprint]

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    openai_api_key = var.openai_api_key
    gemini_api_key = var.gemini_api_key
    app_domain     = var.domain_name
  })

  tags = ["mealplanner", var.environment]
}
