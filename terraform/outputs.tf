output "droplet_ip" {
  description = "Public IP address of the droplet"
  value       = digitalocean_droplet.mealplanner.ipv4_address
}

output "droplet_id" {
  description = "ID of the droplet"
  value       = digitalocean_droplet.mealplanner.id
}

output "ssh_command" {
  description = "SSH command to connect to the droplet"
  value       = "ssh root@${digitalocean_droplet.mealplanner.ipv4_address}"
}

output "application_url" {
  description = "URL to access the application"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "http://${digitalocean_droplet.mealplanner.ipv4_address}"
}
