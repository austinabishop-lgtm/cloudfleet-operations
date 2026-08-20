# CloudFleet Operations Platform — Project Summary

## Project Overview

CloudFleet Operations Platform is a cloud engineering and DevOps project designed around real-world transportation and fleet operations.

The project demonstrates how cloud technologies can address challenges involving data consistency, infrastructure deployment, configuration management, monitoring, security, troubleshooting, and operational readiness.

## Problem 1: Data Source Variability

Fleet and mission information can come from different systems using inconsistent formats.

### Solution

I standardized vehicle and mission information using JavaScript Object Notation (JSON).

Standardized data made the information easier for the application to process consistently and reduced the risk of errors caused by different data structures.

The Flask application used this standardized data to display fleet information and operational readiness through the CloudFleet dashboard.

## Problem 2: Proactive Monitoring and Observability

Waiting for users to report a system problem creates a reactive support model.

### Solution

I implemented Amazon CloudWatch monitoring for the CloudFleet Amazon Elastic Compute Cloud (Amazon EC2) instance.

A CloudWatch alarm named `CloudFleet-High-CPU` monitored average CPU utilization.

The alarm was configured with:

- Metric: CPUUtilization
- Statistic: Average
- Period: 5 minutes
- Threshold: Greater than 70%

After CloudWatch collected sufficient data, the alarm entered the `OK` state.

This demonstrated proactive monitoring of infrastructure health.

## Infrastructure Automation

I used Terraform Infrastructure as Code (IaC) to provision the AWS infrastructure required for CloudFleet.

Terraform managed resources including:

- Amazon EC2 instance
- Security group
- SSH key pair

Using Terraform made the infrastructure repeatable and allowed the environment to be safely destroyed after testing.

## Configuration Management

I used Ansible to remotely configure the EC2 server.

Ansible automated tasks including:

- Connecting to the EC2 instance
- Updating Ubuntu packages
- Installing Docker
- Starting and enabling Docker
- Preparing the server for CloudFleet

Successful Ansible connectivity was verified using the ping module.

## Containerization

I packaged the CloudFleet Python Flask application into a Docker image.

The application was deployed as a Docker container on the EC2 instance and exposed through TCP port 5000.

Application availability was verified with an HTTP request that returned:

`HTTP/1.1 200 OK`

## Security

The project included several security practices.

SSH access was restricted from `0.0.0.0/0` to a specific administrator public IPv4 address using a `/32` Classless Inter-Domain Routing (CIDR) block.

SSH key authentication was used instead of password authentication.

Terraform state files and sensitive local infrastructure files were excluded from Git version control.

## Troubleshooting

Twelve troubleshooting scenarios were documented during the project.

Examples included:

- Docker permission problems
- Terraform output issues
- AWS route-table investigation
- SSH connection timeouts
- EC2 Instance Connect diagnostics
- Windows versus Windows Subsystem for Linux networking
- SSH IPQoS troubleshooting
- Security group hardening
- Ansible connectivity recovery
- Editing files from the wrong host
- Accidental combined terminal commands
- AWS Command Line Interface CloudWatch command troubleshooting

Each incident was documented using:

Problem → Investigation → Resolution → Lesson Learned

## Results

CloudFleet successfully demonstrated an end-to-end cloud engineering workflow:

Standardized Data → Flask → Docker → Terraform → AWS EC2 → Ansible → CloudWatch → Troubleshooting → Git/GitHub

The application was successfully deployed to AWS, returned an HTTP 200 response, was monitored through CloudWatch, documented in GitHub, and ultimately destroyed using Terraform to prevent unnecessary cloud costs.

## Skills Demonstrated

- Amazon Web Services
- Amazon EC2
- Amazon CloudWatch
- Terraform
- Infrastructure as Code
- Ansible
- Docker
- Python
- Flask
- JSON
- Linux
- SSH
- Cloud networking
- Security groups
- Git
- GitHub
- Monitoring and observability
- Technical documentation
- Systematic troubleshooting
