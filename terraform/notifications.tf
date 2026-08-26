resource "aws_sns_topic" "cloudfleet_alerts" {
  name         = "cloudfleet-alerts"
  display_name = "CloudFleet Alerts"

  tags = {
    Name    = "cloudfleet-alerts"
    Project = "CloudFleet"
  }
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.cloudfleet_alerts.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
