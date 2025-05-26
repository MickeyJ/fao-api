provider "aws" {
  region = "us-west-2" # Change to your region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "aurora" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 8.0"

  name           = "food-db"
  database_name  = "fooddb"
  engine         = "aurora-postgresql"
  engine_version = "15.4"
  instance_class = "db.serverless"
  serverlessv2_scaling_configuration = {
    min_capacity = 0.5
    max_capacity = 1
  }

  vpc_id  = data.aws_vpc.default.id
  subnets = data.aws_subnets.default.ids

  instances = {
    food-db-instance = {
      instance_class      = "db.serverless"
      publicly_accessible = true
    }
  }
  create_db_subnet_group = true
  create_security_group  = true

  kms_key_id          = null
  storage_encrypted   = true
  apply_immediately   = true
  skip_final_snapshot = true

  master_username             = "postgres"
  master_password             = var.db_password
  manage_master_user_password = false

  enabled_cloudwatch_logs_exports = [] # Don’t log queries unless needed
  create_monitoring_role          = false
  monitoring_interval             = 0 # No enhanced monitoring

  # Optional: no backtracking (costs $)
  backtrack_window = 0
}

resource "aws_security_group_rule" "aurora_access" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = [var.any_ip]
  security_group_id = module.aurora.security_group_id
}
