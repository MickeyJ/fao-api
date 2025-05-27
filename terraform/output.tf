
output "app_runner_url" {
  value = "https://${aws_apprunner_service.food_data_api.service_url}"
}

# Output the role ARN for debugging
output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}