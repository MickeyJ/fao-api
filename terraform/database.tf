
# Store database password securely
resource "aws_ssm_parameter" "supabase_password" {
  name  = "/food-data-api/db-password"
  type  = "SecureString"
  value = var.db_password # References your existing db_password variable
}