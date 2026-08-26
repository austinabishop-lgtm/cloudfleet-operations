# CloudFleet Screenshot and Evidence Guide

This guide catalogs the strongest portfolio evidence from the CloudFleet Operations Platform project.

Screenshots should demonstrate an engineering result, verification step, troubleshooting decision, or operational capability. They should not expose credentials or unnecessary personal information.

## Privacy Checklist

Before publishing a screenshot, crop or blur:

* Personal email addresses
* AWS account numbers
* Full Amazon Resource Names (ARNs)
* Access keys, tokens, passwords, and private keys
* SSH private-key contents
* Browser bookmarks containing personal information
* Unrelated browser tabs
* Home-directory details when they provide no technical value

Public EC2 addresses may be replaced by the time the environment is destroyed, but they can still be blurred when they are not necessary to understand the evidence.

## Existing Repository Screenshots

### 01 — Standardized Data Validation

**File:** `docs/screenshots/data-validation.png`

**Title:** CloudFleet JSON Data Validation

**Caption:** Validated standardized JavaScript Object Notation (JSON) vehicle and mission datasets before application processing, reducing the risk of failures caused by malformed operational data.

**Demonstrates:** JSON validation, data quality, standardized logistics records, and command-line verification.

### 02 — Local Operations Dashboard

**File:** `docs/screenshots/cloudfleet-dashboard-local.png`

**Title:** CloudFleet Dashboard Running Locally

**Caption:** Developed and tested a Python Flask operations dashboard that converts standardized vehicle and mission data into fleet-readiness metrics, mission visibility, maintenance status, and operational alerts.

**Demonstrates:** Python, Flask, application development, data processing, and logistics-domain knowledge.

### 03 — Docker HTTP Verification

**File:** `docs/screenshots/docker-http-verification.png`

**Title:** CloudFleet Docker Container Verification

**Caption:** Built and ran CloudFleet as a Docker container and verified successful application availability through an HTTP `200 OK` response on TCP port 5000.

**Demonstrates:** Docker, container networking, HTTP testing, and deployment verification.

### 04 — Terraform Plan

**File:** `docs/screenshots/terraform-plan.png`

**Title:** CloudFleet Terraform Infrastructure Plan

**Caption:** Reviewed the Terraform execution plan before deployment to confirm the intended Amazon Elastic Compute Cloud (Amazon EC2), security-group, and SSH key-pair resources would be created without modifying unrelated infrastructure.

**Demonstrates:** Terraform, Infrastructure as Code (IaC), change review, and deployment safety.

### 05 — Ansible Connectivity

**File:** `docs/screenshots/ansible-connectivity.png`

**Title:** CloudFleet Ansible Connectivity Verified

**Caption:** Verified authenticated remote automation access to the CloudFleet EC2 instance using the Ansible ping module before applying server configuration.

**Demonstrates:** Ansible, Secure Shell (SSH), inventory configuration, and predeployment testing.

### 06 — SSH Troubleshooting Resolution

**File:** `docs/screenshots/ssh-troubleshooting-resolution.png`

**Title:** CloudFleet SSH Connectivity Restored

**Caption:** Restored reliable SSH access after validating EC2 health, security-group rules, routing, local network behavior, and SSH client settings, then applying the Internet Protocol Quality of Service (IPQoS) workaround.

**Demonstrates:** Structured troubleshooting, AWS networking, Linux administration, SSH, and evidence-based diagnosis.

### 07 — CloudFleet on AWS

**File:** `docs/screenshots/cloudfleet-dashboard-aws.png`

**Title:** CloudFleet Operations Platform Deployed to AWS

**Caption:** Successfully deployed the CloudFleet fleet-readiness dashboard as a containerized application on Amazon EC2, displaying vehicle availability, active missions, maintenance requirements, and operational alerts.

**Demonstrates:** End-to-end cloud deployment and the connection between logistics experience and cloud engineering.

### 08 — CloudWatch Alarm

**File:** `docs/screenshots/cloudwatch-alarm.png`

**Title:** CloudFleet CloudWatch Alarm in Healthy State

**Caption:** Verified proactive Amazon CloudWatch monitoring for the CloudFleet EC2 workload, including threshold configuration and a healthy `OK` alarm state.

**Demonstrates:** Monitoring, alert thresholds, infrastructure health, and observability.

### 09 — Final Health Verification

**File:** `docs/screenshots/final-health-verification.png`

**Title:** CloudFleet Application and Monitoring Health Verified

**Caption:** Confirmed that the deployed CloudFleet application returned an HTTP `200 OK` response and that its CloudWatch monitoring remained in a healthy state.

**Demonstrates:** Layered verification across the application and monitoring components.

## Final Screenshots to Add

### 10 — Gunicorn Production Runtime

**Recommended file:** `docs/screenshots/gunicorn-deployment-verification.png`

**Title:** CloudFleet Gunicorn Deployment Verified

**Caption:** Rebuilt and redeployed CloudFleet with Flask debug mode disabled and Gunicorn serving the application through multiple workers, then verified the public endpoint returned `HTTP/1.1 200 OK`.

**Suggested evidence:** Terminal output showing the Gunicorn server header, running Docker container, and healthy worker startup logs.

### 11 — CloudWatch Operations Dashboard

**Recommended file:** `docs/screenshots/cloudwatch-operations-dashboard.png`

**Title:** CloudFleet CloudWatch Operations Dashboard

**Caption:** Created an Amazon CloudWatch operations dashboard through Terraform to visualize EC2 processor utilization, status-check failures, and incoming and outgoing network traffic.

**Suggested evidence:** The AWS CloudWatch dashboard displaying all three metric widgets.

### 12 — SNS Email Notification

**Recommended file:** `docs/screenshots/sns-email-notification-test.png`

**Title:** CloudFleet SNS Email Alert Delivery Verified

**Caption:** Verified end-to-end Amazon Simple Notification Service (Amazon SNS) email delivery using a controlled CloudFleet test message. Both CloudWatch alarms publish incident and recovery notifications to the confirmed subscription.

**Suggested evidence:** The received test email with the personal address, AWS account number, topic ARN, and message identifier cropped or blurred.

## Optional Additional Evidence

### 13 — Ansible Idempotency

**Recommended file:** `docs/screenshots/ansible-idempotency.png`

**Title:** CloudFleet Ansible Deployment Is Idempotent

**Caption:** Repeated the CloudFleet Ansible deployment with `changed=0`, `unreachable=0`, and `failed=0`, demonstrating that the automation maintained the desired configuration without unnecessary changes.

### 14 — Terraform Drift Check

**Recommended file:** `docs/screenshots/terraform-no-changes.png`

**Title:** CloudFleet Terraform Drift Check

**Caption:** Verified that the live AWS environment matched the Terraform configuration, producing a no-change execution plan after deployment.

## Recommended GitHub Selection

The main README should display only the strongest images:

1. CloudFleet dashboard deployed to AWS
2. CloudWatch operations dashboard
3. Ansible idempotency
4. SNS email notification verification

The remaining screenshots provide detailed evidence through this guide without making the main README excessively long.

## Screenshot Quality Standards

Use the following standards for portfolio screenshots:

* Crop to the relevant technical evidence.
* Use readable zoom and resolution.
* Keep the command and result visible together.
* Remove unrelated tabs and desktop clutter.
* Never expose secrets or private keys.
* Use consistent lowercase filenames with hyphens.
* Add a concise caption explaining the action, tool, and verified result.
* Preserve failure screenshots when they support a troubleshooting story.
