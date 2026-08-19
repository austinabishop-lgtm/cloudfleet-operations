data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "cloudfleet" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.cloudfleet_key.key_name
  vpc_security_group_ids = [aws_security_group.cloudfleet_sg.id]

  tags = {
    Name    = "cloudfleet-server"
    Project = "CloudFleet"
  }
}
