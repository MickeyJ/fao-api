output "aurora_endpoint" {
  value = module.aurora.cluster_endpoint
}

output "aurora_reader_endpoint" {
  value = module.aurora.cluster_reader_endpoint
}

output "app_runner_url" {
  value = "https://${aws_apprunner_service.food_data_api.service_url}"
}