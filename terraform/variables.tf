variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key file"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc3"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "openai_api_key" {
  description = "OpenAI API key for recipe parsing"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Google Gemini API key (optional)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "domain_name" {
  description = "Custom domain name (optional, leave empty to use IP)"
  type        = string
  default     = ""
}
