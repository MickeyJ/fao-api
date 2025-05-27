
output "app_runner_url" {
  value = "https://${aws_apprunner_service.food_data_api.service_url}"
}