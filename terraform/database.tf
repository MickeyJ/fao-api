
# Store database password securely
resource "aws_ssm_parameter" "supabase_password" {
  name  = "/food-data-api/db-password"
  type  = "SecureString"
  value = var.db_password # References your existing db_password variable
}

resource "aws_ssm_parameter" "redis_password" {
  name  = "/food-data-api/redis-password"
  type  = "SecureString"
  value = var.redis_password
}