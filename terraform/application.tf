# ECR Repository for your container images
resource "aws_ecr_repository" "fao_api" {
  name                 = "fao-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM Role for App Runner Instance (to read secrets)
resource "aws_iam_role" "app_runner_instance_role" {
  name = "fao-api-apprunner-instance-role"

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
  name = "fao-api-ssm-access"
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
        Resource = "arn:aws:ssm:us-west-2:*:parameter/fao-api/*"
      }
    ]
  })
}

# IAM Role for App Runner Access (to pull from ECR)
resource "aws_iam_role" "app_runner_access_role" {
  name = "fao-api-apprunner-access-role"

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
resource "aws_apprunner_service" "fao_api" {
  service_name = "fao-api"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.app_runner_access_role.arn
    }
    image_repository {
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          DB_HOST    = aws_db_instance.fao_postgres.address
          DB_PORT    = "5432"
          DB_NAME    = aws_db_instance.fao_postgres.db_name
          DB_USER    = aws_db_instance.fao_postgres.username
          REDIS_HOST = "romantic-swine-11670.upstash.io"
          REDIS_PORT = "6379"
        }

        runtime_environment_secrets = {
          DB_PASSWORD    = aws_ssm_parameter.rds_db_password.arn
          REDIS_PASSWORD = aws_ssm_parameter.redis_password.arn
        }
      }
      image_identifier      = "${aws_ecr_repository.fao_api.repository_url}:latest"
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
    Name = "fao-api"
  }

  # CRITICAL: Ensure roles are created before App Runner
  depends_on = [
    aws_ecr_repository.fao_api,
    aws_iam_role.app_runner_access_role,
    aws_iam_role_policy_attachment.app_runner_access_role,
    aws_iam_role.app_runner_instance_role,
    aws_iam_role_policy.app_runner_instance_policy,
    aws_db_instance.fao_postgres,
    aws_ssm_parameter.rds_db_password
  ]
}