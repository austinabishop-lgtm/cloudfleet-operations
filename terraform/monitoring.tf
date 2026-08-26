resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "cloudfleet-high-cpu"
  alarm_description   = "CloudFleet EC2 average CPU utilization is at least 70 percent"
  alarm_actions       = [aws_sns_topic.cloudfleet_alerts.arn]
  ok_actions          = [aws_sns_topic.cloudfleet_alerts.arn]
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  datapoints_to_alarm = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 70
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = aws_instance.cloudfleet.id
  }

  tags = {
    Name    = "cloudfleet-high-cpu"
    Project = "CloudFleet"
  }
}

resource "aws_cloudwatch_metric_alarm" "status_check_failed" {
  alarm_name          = "cloudfleet-status-check-failed"
  alarm_description   = "CloudFleet EC2 instance or system status check has failed"
  alarm_actions       = [aws_sns_topic.cloudfleet_alerts.arn]
  ok_actions          = [aws_sns_topic.cloudfleet_alerts.arn]
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  datapoints_to_alarm = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = aws_instance.cloudfleet.id
  }

  tags = {
    Name    = "cloudfleet-status-check-failed"
    Project = "CloudFleet"
  }
}

resource "aws_cloudwatch_dashboard" "cloudfleet" {
  dashboard_name = "CloudFleet-Operations"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          title  = "CloudFleet EC2 CPU Utilization"
          region = "us-east-1"
          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/EC2",
              "CPUUtilization",
              "InstanceId",
              aws_instance.cloudfleet.id
            ]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          title  = "CloudFleet EC2 Status Checks"
          region = "us-east-1"
          period = 60
          stat   = "Maximum"

          metrics = [
            [
              "AWS/EC2",
              "StatusCheckFailed",
              "InstanceId",
              aws_instance.cloudfleet.id
            ]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          title  = "CloudFleet Network Traffic"
          region = "us-east-1"
          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/EC2",
              "NetworkIn",
              "InstanceId",
              aws_instance.cloudfleet.id,
              {
                label = "Network In"
              }
            ],
            [
              "AWS/EC2",
              "NetworkOut",
              "InstanceId",
              aws_instance.cloudfleet.id,
              {
                label = "Network Out"
              }
            ]
          ]
        }
      }
    ]
  })
}
