# ECR Repository for your container images
resource "aws_ecr_repository" "food_data_api" {
  name                 = "food-data-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM Role for App Runner Instance (to read secrets)
resource "aws_iam_role" "app_runner_instance_role" {
  name = "food-data-api-apprunner-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "app_runner_instance_policy" {
  name = "food-data-api-ssm-access"
  role = aws_iam_role.app_runner_instance_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:us-west-2:*:parameter/food-data-api/*"
      }
    ]
  })
}

# IAM Role for App Runner Access (to pull from ECR)
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

# App Runner Service
resource "aws_apprunner_service" "food_data_api" {
  service_name = "food-data-api"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.app_runner_access_role.arn
    }
    image_repository {
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          DB_HOST = "aws-0-us-west-1.pooler.supabase.com"
          DB_PORT = "5432"
          DB_NAME = "postgres"
          DB_USER = "postgres.rltlqzgjokukrrpqqvre"
          REDIS_HOST = "romantic-swine-11670.upstash.io"
          REDIS_PORT = "6379"
        }

        runtime_environment_secrets = {
          DB_PASSWORD = aws_ssm_parameter.supabase_password.arn
          REDIS_PASSWORD = aws_ssm_parameter.redis_password.arn
        }
      }
      image_identifier      = "${aws_ecr_repository.food_data_api.repository_url}:latest"
      image_repository_type = "ECR"
    }
    auto_deployments_enabled = false # Manual deployments for now
  }

  instance_configuration {
    cpu               = "0.5 vCPU" # 0.5 vCPU
    memory            = "1 GB"     # 1 GB RAM
    instance_role_arn = aws_iam_role.app_runner_instance_role.arn
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

  # CRITICAL: Ensure roles are created before App Runner
  depends_on = [
    aws_ecr_repository.food_data_api,
    aws_iam_role.app_runner_access_role,
    aws_iam_role_policy_attachment.app_runner_access_role,
    aws_iam_role.app_runner_instance_role,
    aws_iam_role_policy.app_runner_instance_policy,
    aws_ssm_parameter.supabase_password
  ]
}