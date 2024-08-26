resource "aws_security_group" "chalice" {
  name        = "${var.project_name}-chalice-sg"
  description = "Security group for Chalice functions"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-chalice-sg"
  }
}
