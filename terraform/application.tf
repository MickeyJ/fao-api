
# ECR Repository for your container images
resource "aws_ecr_repository" "food_data_api" {
  name                 = "food-data-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM Role for App Runner
resource "aws_iam_role" "app_runner_access_role" {
  name = "food-data-api-apprunner-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app_runner_access_role" {
  role       = aws_iam_role.app_runner_access_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

resource "aws_apprunner_service" "food_data_api" {
  service_name = "food-data-api"

  source_configuration {
    authentication_configuration { # ← The access role goes here
      access_role_arn = aws_iam_role.app_runner_access_role.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.food_data_api.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          DB_HOST = module.aurora.cluster_endpoint
          DB_PORT = "5432"
          DB_NAME = "fooddb"
          DB_USER = "postgres"
        }
        runtime_environment_secrets = {
          DB_PASSWORD = aws_ssm_parameter.db_password.arn
        }
      }
    }

    auto_deployments_enabled = false # Manual deployments for now
  }

  instance_configuration {
    cpu    = "0.5 vCPU" # 0.5 vCPU
    memory = "1 GB"     # 1 GB RAM
  }

  health_check_configuration {
    healthy_threshold   = 1
    interval            = 10
    path                = "/"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 5
  }

  tags = {
    Name = "food-data-api"
  }

  depends_on = [
    aws_ecr_repository.food_data_api, # Ensure ECR exists first
    module.aurora,
    aws_ssm_parameter.db_password # Wait for password to be stored
  ]
}

