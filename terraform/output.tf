
output "app_runner_url" {
  value = "https://${aws_apprunner_service.fao_api.service_url}"
}

# Output the role ARN for debugging
output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}

# RDS Outputs
output "rds_endpoint" {
  value       = aws_db_instance.fao_postgres.endpoint
  description = "RDS instance endpoint"
}

output "rds_address" {
  value       = aws_db_instance.fao_postgres.address
  description = "RDS instance hostname"
}

output "rds_database_name" {
  value       = aws_db_instance.fao_postgres.db_name
  description = "Database name"
}

output "rds_username" {
  value       = aws_db_instance.fao_postgres.username
  description = "Master username"
  sensitive   = true
}

output "rds_password_ssm_path" {
  value       = aws_ssm_parameter.rds_db_password.name
  description = "SSM parameter path for RDS password"
}

# EC2 Outputs
output "bastion_public_ip" {
  value = aws_instance.bastion.public_ip
}

output "bastion_ssh_command" {
  value = "ssh -i terraform/bastion-key.pem ec2-user@${aws_instance.bastion.public_ip}"
}
output "bastion_role_arn" {
  value = aws_iam_role.bastion_role.arn
}