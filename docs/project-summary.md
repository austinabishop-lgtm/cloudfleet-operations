k# CloudFleet Operations Platform — Project Summary

## Overview

CloudFleet Operations Platform is an end-to-end cloud engineering and DevOps project inspired by real-world transportation, dispatch, vehicle accountability, and mission-readiness operations.

The project converts standardized fleet and mission data into a containerized web dashboard deployed to Amazon Web Services (AWS). Terraform provisions the infrastructure, Ansible configures and deploys the server, Amazon CloudWatch monitors the environment, and Amazon Simple Notification Service (Amazon SNS) delivers email alerts.

## Business Problem

Transportation organizations may receive vehicle, dispatch, maintenance, and mission information from multiple systems. Inconsistent field names, formats, and status values can reduce data quality and make automation unreliable.

Operations teams also need more than a working application. They need repeatable deployment, health verification, monitoring, alerting, secure administration, and documented recovery procedures.

## Solution

CloudFleet provides this complete workflow:

Standardized fleet data → Python and Flask dashboard → Docker and Gunicorn → Ansible deployment → Amazon EC2 → CloudWatch monitoring → Amazon SNS email alerts

## Data Standardization

Vehicle and mission records use standardized JavaScript Object Notation (JSON) structures.

Vehicle data includes:

* Vehicle identifier
* Vehicle type
* Operational status
* Current location
* Maintenance requirement

Mission data includes:

* Mission identifier
* Assigned vehicle
* Driver
* Destination
* Priority
* Mission status

Approved values improve application reliability, validation, troubleshooting, and future system integration.

## Application Development

The Python Flask application reads the standardized fleet datasets and calculates:

* Total vehicles
* Available vehicles
* Dispatched vehicles
* Vehicles in maintenance
* Fleet availability
* Operational alerts

The dashboard displays mission assignments, vehicle status, locations, priorities, and maintenance requirements.

A dedicated `/health` route returns a machine-readable response showing that the CloudFleet service is healthy.

## Containerization and Runtime Hardening

The application is packaged as a Docker image.

The original Flask development server was replaced with Gunicorn, a production-oriented Web Server Gateway Interface (WSGI) server. Debug mode was disabled, dependency versions were pinned, and the container was configured to restart unless intentionally stopped.

The deployed application was verified through Gunicorn with an HTTP `200 OK` response.

## Infrastructure Automation

Terraform Infrastructure as Code (IaC) manages:

* Amazon Elastic Compute Cloud (Amazon EC2) instance
* Security group
* SSH key-pair registration
* CloudWatch alarms
* CloudWatch operations dashboard
* SNS topic
* Email subscription

Terraform validation succeeded, and the final plan reported:

`No changes. Your infrastructure matches the configuration.`

This confirmed that the deployed infrastructure matched the declared configuration.

## Configuration Management

Ansible automates:

* Ubuntu package-cache updates
* Docker installation
* Docker service management
* User group configuration
* Application-directory creation
* Source and data transfer
* Conditional Docker image builds
* Container replacement and startup
* Application health verification

A repeated Ansible run completed with `changed=0`, `unreachable=0`, and `failed=0`, demonstrating idempotent configuration management.

## Monitoring and Observability

The `CloudFleet-Operations` CloudWatch dashboard displays:

* Average processor utilization
* EC2 status-check failures
* Incoming network traffic
* Outgoing network traffic

CloudFleet includes two automated alarms:

1. `cloudfleet-high-cpu` monitors sustained processor utilization at or above 70 percent.
2. `cloudfleet-status-check-failed` monitors EC2 instance or AWS system-check failures.

Both alarms reached the healthy `OK` state after CloudWatch collected sufficient data.

## Email Notifications

The CloudWatch alarms publish both incident and recovery events to the `cloudfleet-alerts` SNS topic.

A confirmed email subscription receives those notifications. End-to-end delivery was verified using a controlled SNS test message without generating a real infrastructure incident.

The notification email is provided through an ignored Terraform variable file and is not stored in the public repository.

## Security

Security measures include:

* ED25519 Secure Shell (SSH) key authentication
* SSH restricted to one administrator IPv4 `/32` Classless Inter-Domain Routing (CIDR) address
* Terraform state excluded from Git
* Sensitive `.tfvars` files excluded from Git
* Local private keys excluded from Git
* Flask debug mode disabled
* Gunicorn used for the deployed runtime
* Infrastructure changes reviewed before application

The current portfolio deployment uses HTTP on port `5000`. A production enhancement would add an Application Load Balancer, Transport Layer Security (TLS), a managed certificate, and a domain name.

## Verification

The environment was verified through:

* Terraform formatting, validation, planning, and drift detection
* Ansible syntax checks
* Ansible deployment and idempotency testing
* Remote Docker service and container checks
* Public dashboard HTTP checks
* Dedicated `/health` endpoint checks
* CloudWatch alarm-state checks
* CloudWatch dashboard visualization
* Controlled SNS email-delivery testing
* Git staged-diff and sensitive-data checks

## Troubleshooting

The project generated practical troubleshooting experience across several layers:

* Docker permissions
* Terraform state and working directories
* AWS networking
* Dynamic public addresses
* Virtual Private Network (VPN) changes
* Cellular tethering
* Security-group rules
* SSH transport behavior
* Ansible check mode
* Flask runtime security
* Python environments
* AWS Command Line Interface (AWS CLI) compatibility
* Terminal pager behavior
* SNS testing

Each incident follows this structure:

Problem → Evidence → Root Cause → Resolution → Verification → Lesson

## Results

CloudFleet successfully demonstrated:

* A working logistics-focused web application
* Standardized operational data
* Containerized deployment
* Repeatable AWS infrastructure
* Automated server configuration
* Idempotent deployment
* Dedicated health monitoring
* Infrastructure observability
* Automated incident and recovery notifications
* Secure remote administration
* Systematic troubleshooting
* Version-controlled technical documentation

## Skills Demonstrated

* Amazon Web Services
* Amazon EC2
* Amazon CloudWatch
* Amazon SNS
* Terraform
* Infrastructure as Code
* Ansible
* Docker
* Gunicorn
* Python
* Flask
* JSON
* Linux
* SSH
* Cloud networking
* Security groups
* Monitoring and observability
* Git and GitHub
* Troubleshooting
* Technical documentation
* Cost-aware resource management

## Portfolio Status

The application and operational tooling have been successfully deployed and verified. The temporary AWS environment remains active only while final portfolio evidence is collected.

After documentation is complete, Terraform will destroy the managed resources to prevent unnecessary cloud charges. Cleanup will be verified by confirming that the Terraform state contains no remaining resources.
