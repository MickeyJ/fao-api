
resource "aws_ssm_parameter" "redis_password" {
  name  = "/fao-api/redis-password"
  type  = "SecureString"
  value = var.redis_password
}

# Password resources first
resource "random_password" "rds_password" {
  length  = 32
  special = false
}

resource "aws_ssm_parameter" "rds_db_password" {
  name  = "/fao-api/rds-password"
  type  = "SecureString"
  value = random_password.rds_password.result
}

# Data source to get default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source to get subnets in default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Subnet group for RDS
resource "aws_db_subnet_group" "fao_rds" {
  name       = "fao-api-rds-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "fao-api-rds-subnet-group"
  }
}

# Security group for RDS
resource "aws_security_group" "fao_rds" {
  name        = "fao-api-rds-sg"
  description = "Security group for FAO API RDS instance"
  vpc_id      = data.aws_vpc.default.id

  # This allows connections FROM your VPC
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  # ADD THIS - allows connections from ANYWHERE
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Public access to RDS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "fao-api-rds-sg"
  }
}

resource "aws_db_instance" "fao_postgres" {
  identifier = "fao-api-db" # matches your naming convention

  # Basic config
  engine         = "postgres"
  engine_version = "15.13"
  instance_class = "db.t3.medium"

  # Storage
  allocated_storage = 50
  storage_type      = "gp3"
  storage_encrypted = true

  # Database
  db_name  = "fao"
  username = "faoadmin"
  password = aws_ssm_parameter.rds_db_password.value

  # Add this networking section:
  db_subnet_group_name   = aws_db_subnet_group.fao_rds.name
  vpc_security_group_ids = [aws_security_group.fao_rds.id]
  publicly_accessible    = true

  # Backup
  backup_retention_period = 7
  backup_window           = "03:00-04:00"         # 3-4 AM UTC
  maintenance_window      = "sun:04:00-sun:05:00" # Sunday 4-5 AM UTC

  # Performance
  performance_insights_enabled          = true
  performance_insights_retention_period = 7 # Free tier

  # Final snapshot
  skip_final_snapshot       = false
  final_snapshot_identifier = "fao-api-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = {
    Name = "fao-api-db"
  }

}