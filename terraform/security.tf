resource "aws_security_group" "cloudfleet_sg" {
  name        = "cloudfleet-sg"
  description = "Allow SSH and CloudFleet web traffic"

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["190.140.22.86/32"]
  }

  ingress {
    description = "CloudFleet web access"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "cloudfleet-sg"
    Project = "CloudFleet"
  }
}
