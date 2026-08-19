resource "aws_key_pair" "cloudfleet_key" {
  key_name   = "cloudfleet-key"
  public_key = file("~/.ssh/cloudfleet-key.pub")

  tags = {
    Name    = "cloudfleet-key"
    Project = "CloudFleet"
  }
}
