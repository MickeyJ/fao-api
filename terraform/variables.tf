
variable "db_password" {
  type      = string
  sensitive = true
}

variable "any_ip" {
  type    = string
  default = "0.0.0.0/0" # Or better: your personal IP for dev access
}
