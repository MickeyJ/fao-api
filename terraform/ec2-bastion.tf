# IAM role for bastion
resource "aws_iam_role" "bastion_role" {
  name = "fao-api-bastion-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for bastion (S3 access for dumps, RDS access)
resource "aws_iam_role_policy" "bastion_policy" {
  name = "fao-api-bastion-policy"
  role = aws_iam_role.bastion_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::*/*", # Or restrict to specific bucket
          "arn:aws:s3:::*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters"
        ]
        Resource = "*"
      }
    ]
  })
}

# Instance profile for bastion
resource "aws_iam_instance_profile" "bastion_profile" {
  name = "fao-api-bastion-profile"
  role = aws_iam_role.bastion_role.name
}

# Generate SSH key pair
resource "tls_private_key" "bastion_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "bastion_key" {
  key_name   = "fao-api-bastion-key"
  public_key = tls_private_key.bastion_key.public_key_openssh
}

# Save private key locally
resource "local_file" "bastion_key" {
  content         = tls_private_key.bastion_key.private_key_pem
  filename        = "${path.module}/bastion-key.pem"
  file_permission = "0600"
}

# Security group for bastion
resource "aws_security_group" "bastion_sg" {
  name        = "fao-api-bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Or restrict to your IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "fao-api-bastion-sg"
  }
}

resource "aws_instance" "bastion" {
  ami           = "ami-05f9478b4deb8d173" # Amazon Linux 2023 x86_64
  instance_type = "t3.micro"

  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
  subnet_id                   = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true

  key_name             = aws_key_pair.bastion_key.key_name
  iam_instance_profile = aws_iam_instance_profile.bastion_profile.name

  user_data = <<-EOF
    #!/bin/bash
    set -ex
    
    # Log output
    exec > >(tee /var/log/user-data.log)
    exec 2>&1
    
    # Update system
    dnf update -y
    
    # AWS CLI is pre-installed on AL2023
    aws --version
    
    # Install PostgreSQL 17 client from Amazon Linux repos
    sudo dnf install -y postgresql17
    
    # Verify installations
    which aws
    which psql
    psql --version
    pg_restore --version
    
    # Set default region
    aws configure set default.region us-west-2
    
    echo "Setup complete!"
  EOF

  tags = {
    Name = "fao-api-bastion"
  }
}

