output "cloudfleet_public_ip" {
  description = "Public IP address of the CloudFleet EC2 instance"
  value       = aws_instance.cloudfleet.public_ip
}

output "cloudfleet_instance_id" {
  description = "EC2 instance ID for CloudFleet"
  value       = aws_instance.cloudfleet.id
}

output "cloudfleet_url" {
  description = "CloudFleet application URL"
  value       = "http://${aws_instance.cloudfleet.public_ip}:5000"
}
