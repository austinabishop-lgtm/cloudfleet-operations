# CloudFleet Operations Platform

CloudFleet Operations Platform is an end-to-end cloud engineering and DevOps portfolio project inspired by real-world transportation, dispatch, vehicle accountability, and fleet-readiness operations.

The platform converts standardized vehicle and mission data into a web-based operations dashboard. The application is containerized with Docker, deployed to Amazon Web Services (AWS), automated with Terraform and Ansible, monitored with Amazon CloudWatch, and connected to email notifications through Amazon Simple Notification Service (Amazon SNS).

## Project Outcomes

CloudFleet demonstrates how to:

- Standardize transportation and logistics data with JavaScript Object Notation (JSON)
- Build a fleet-readiness dashboard with Python and Flask
- Package an application into a Docker container
- Serve Flask through the Gunicorn production Web Server Gateway Interface (WSGI) server
- Provision AWS infrastructure with Terraform Infrastructure as Code (IaC)
- Configure and deploy an Amazon Elastic Compute Cloud (Amazon EC2) server with Ansible
- Verify application health through an automated `/health` endpoint
- Monitor processor, status-check, and network metrics with Amazon CloudWatch
- Send alarm and recovery emails with Amazon SNS
- Restrict Secure Shell (SSH) administration to a single public IPv4 address
- Troubleshoot failures across application, operating-system, network, automation, and cloud layers
- Verify repeatability through Terraform drift detection and Ansible idempotency

## Business Context

Transportation teams depend on accurate information about vehicle availability, active missions, maintenance requirements, drivers, destinations, and operational readiness.

When information comes from different systems using inconsistent formats, teams may experience:

- Incorrect vehicle status
- Delayed missions
- Incomplete maintenance visibility
- Reduced fleet readiness
- Data-processing failures
- Difficult system integration

CloudFleet addresses this problem by defining consistent vehicle and mission data structures and presenting the information through a centralized dashboard.

## Architecture

```text
Administrator Workstation
        |
        | Terraform
        v
+-----------------------------+
| Amazon Web Services         |
|                             |
|  Security Group             |
|    |                        |
|    v                        |
|  Amazon EC2 (Ubuntu)        |
|    |                        |
|    v                        |
|  Docker Container           |
|    |                        |
|    v                        |
|  Gunicorn + Flask           |
|    |                        |
|    v                        |
|  CloudFleet Dashboard       |
+-----------------------------+
        |
        | Metrics
        v
Amazon CloudWatch
   |             |
   |             +--> Operations Dashboard
   |
   +--> CPU Alarm
   +--> Status-Check Alarm
              |
              v
        Amazon SNS
              |
              v
       Email Notification
```

### Deployment Flow

```text
Standardized JSON data
        |
        v
Python and Flask application
        |
        v
Docker image
        |
        v
Ansible configuration and deployment
        |
        v
Amazon EC2
        |
        v
Gunicorn application service
        |
        v
Health checks and CloudWatch monitoring
        |
        v
Amazon SNS email alerts
```

## Technologies

| Technology | Purpose |
|---|---|
| AWS | Cloud platform |
| Amazon EC2 | Hosts the application server |
| Amazon CloudWatch | Provides metrics, alarms, and the operations dashboard |
| Amazon SNS | Delivers alarm and recovery email notifications |
| Terraform | Provisions and manages cloud infrastructure as code |
| Ansible | Configures the server and deploys the application |
| Docker | Packages the application and its dependencies |
| Gunicorn | Runs the Flask application with production-oriented workers |
| Python | Implements application logic |
| Flask | Provides web routes and dashboard rendering |
| JSON | Standardizes vehicle and mission records |
| Ubuntu Linux | Provides the EC2 server operating system |
| SSH | Provides authenticated remote administration |
| Git and GitHub | Provide version control and portfolio hosting |
| Windows Subsystem for Linux (WSL) | Provides the local Linux development environment |

## Data Standardization

CloudFleet defines consistent JSON fields and approved status values for vehicle and mission records.

Example vehicle record:

```json
{
  "vehicle_id": "V-001",
  "type": "Cargo Van",
  "status": "dispatched",
  "location": "Warehouse A",
  "maintenance_required": false
}
```

Example mission record:

```json
{
  "mission_id": "M-1001",
  "vehicle_id": "V-001",
  "driver": "Johnson",
  "destination": "Warehouse A",
  "priority": "high",
  "status": "in_progress"
}
```

Standardization improves consistency, validation, automation, troubleshooting, and future integration with Application Programming Interfaces (APIs) or databases.

See [docs/data-standard.md](docs/data-standard.md) for the complete standard.

## Application Features

The CloudFleet dashboard provides:

- Total vehicle count
- Available vehicle count
- Dispatched vehicle count
- Maintenance vehicle count
- Active mission visibility
- Vehicle location and status
- Maintenance indicators
- Low-availability alerts

The application also provides a machine-readable health endpoint:

```text
GET /health
```

Successful response:

```json
{
  "service": "cloudfleet",
  "status": "healthy"
}
```

## Containerization and Application Hardening

The application runs inside a Docker container built from `python:3.14-slim`.

The container:

- Installs pinned Flask and Gunicorn dependencies
- Copies the application and standardized data
- Exposes Transmission Control Protocol (TCP) port `5000`
- Starts two Gunicorn workers with two threads each
- Uses a 60-second worker timeout
- Restarts automatically unless intentionally stopped

Application startup command:

```text
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 --timeout 60 app.app:app
```

The Flask development debugger is disabled in the deployed environment.

## Infrastructure as Code

Terraform provisions and manages:

- One Amazon EC2 `t3.micro` instance
- One EC2 SSH key-pair registration
- One security group
- Two CloudWatch metric alarms
- One CloudWatch operations dashboard
- One SNS topic
- One confirmed email subscription

Typical workflow:

```bash
terraform -chdir=terraform init
terraform -chdir=terraform fmt
terraform -chdir=terraform validate
terraform -chdir=terraform plan
terraform -chdir=terraform apply
```

Terraform outputs return the instance identifier, public IPv4 address, and application URL.

A final Terraform plan produced:

```text
No changes. Your infrastructure matches the configuration.
```

This verified that the deployed resources matched the declared infrastructure code.

## Configuration Management and Deployment

Ansible performs the following operations:

1. Updates the Ubuntu package cache
2. Installs Docker
3. Starts and enables the Docker service
4. Adds the Ubuntu user to the Docker group
5. Creates `/opt/cloudfleet`
6. Copies the Dockerfile, application, and fleet data
7. Builds the image when source files change
8. Replaces an outdated container when necessary
9. Starts or reuses the existing container
10. Verifies the `/health` endpoint

Deployment command:

```bash
ansible-playbook \
  -i ansible/inventory.ini \
  ansible/playbook.yml
```

A repeated playbook run completed with:

```text
changed=0
unreachable=0
failed=0
```

This demonstrated Ansible idempotency: rerunning the automation did not make unnecessary changes.

## Monitoring and Alerting

The `CloudFleet-Operations` CloudWatch dashboard displays:

- Average EC2 processor utilization
- EC2 instance and system status-check failures
- Incoming network traffic
- Outgoing network traffic

Two CloudWatch alarms provide proactive monitoring:

### High Processor Utilization

- Alarm: `cloudfleet-high-cpu`
- Metric: `CPUUtilization`
- Statistic: `Average`
- Threshold: at least 70 percent
- Period: 300 seconds
- Evaluation: two out of two datapoints

### Failed EC2 Status Check

- Alarm: `cloudfleet-status-check-failed`
- Metric: `StatusCheckFailed`
- Statistic: `Maximum`
- Threshold: at least 1
- Period: 60 seconds
- Evaluation: two out of two datapoints

Both alarms publish alarm and recovery events to the `cloudfleet-alerts` SNS topic. A confirmed email subscription receives those notifications.

A controlled SNS test verified end-to-end email delivery without creating a real incident.

## Security Practices

CloudFleet implements the following controls:

- ED25519 SSH public-key authentication
- SSH access restricted to one administrator IPv4 `/32` Classless Inter-Domain Routing (CIDR) address
- Application and administrative ports separated into different security-group rules
- Sensitive notification email stored in an ignored `.tfvars` file
- Terraform state excluded from Git
- Local private SSH key excluded from Git
- Flask debug mode disabled
- Gunicorn used instead of the Flask development server
- Infrastructure changes reviewed through Terraform plans
- Exact files staged for Git commits instead of indiscriminate staging

The application endpoint currently uses HTTP on port `5000`. A production evolution would place the application behind an Application Load Balancer with Transport Layer Security (TLS), a managed certificate, and a domain name.

## Verification

The deployment was verified at multiple layers:

```bash
terraform -chdir=terraform validate
terraform -chdir=terraform plan
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
curl -i http://<EC2-PUBLIC-IP>:5000/health
```

The health endpoint returned:

```text
HTTP/1.1 200 OK
Server: gunicorn
Content-Type: application/json
```

The running container and Docker service were also verified remotely.

## Troubleshooting

The project includes real troubleshooting scenarios involving:

- Docker socket permissions
- Terraform working directories and state
- AWS route-table queries
- Dynamic public IP addresses
- Virtual Private Network (VPN) address changes
- Cellular tethering and egress-address changes
- Security-group SSH rules
- SSH banner and connection timeouts
- SSH Internet Protocol Quality of Service (IPQoS)
- Stale SSH aliases and Ansible inventory
- Ansible check-mode dependency behavior
- Flask development-server exposure
- Missing local Python dependencies
- AWS Command Line Interface (AWS CLI) pager behavior
- Accidental terminal-output files
- AWS CLI and Python 3.14 compatibility
- SNS email-delivery verification

See [docs/troubleshooting.md](docs/troubleshooting.md) for the complete incident record.

## Repository Structure

```text
cloudfleet-operations/
├── ansible/
│   ├── inventory.ini
│   └── playbook.yml
├── app/
│   ├── app.py
│   └── requirements.txt
├── data/
│   ├── missions.json
│   └── vehicles.json
├── docs/
│   ├── data-standard.md
│   ├── project-summary.md
│   └── troubleshooting.md
├── terraform/
│   ├── ec2.tf
│   ├── key.tf
│   ├── main.tf
│   ├── monitoring.tf
│   ├── notifications.tf
│   ├── outputs.tf
│   ├── security.tf
│   └── variables.tf
├── .gitignore
├── Dockerfile
└── README.md
```

## Skills Demonstrated

- AWS infrastructure administration
- Amazon EC2
- Amazon CloudWatch
- Amazon SNS
- Terraform and Infrastructure as Code
- Ansible configuration management
- Docker containerization
- Gunicorn application serving
- Python and Flask
- JSON data modeling
- Linux administration
- Cloud networking and security groups
- SSH authentication and troubleshooting
- Monitoring, alerting, and observability
- Git and GitHub
- Technical documentation
- Systematic incident troubleshooting
- Cost-aware cloud resource management

## Key Engineering Lessons

CloudFleet demonstrates that deploying an application is only one part of cloud engineering. A useful cloud workload must also be:

- Repeatable
- Secure
- Observable
- Recoverable
- Testable
- Troubleshootable
- Documented
- Cost-aware

## Current Status

CloudFleet has been successfully deployed and verified on AWS. The application, health check, CloudWatch dashboard, alarms, and SNS email-notification path have all been tested.

The environment is temporary and will be destroyed with Terraform after final portfolio evidence is captured to prevent unnecessary AWS charges.

## Cleanup

Review the destruction plan before approving it:

```bash
terraform -chdir=terraform plan -destroy
terraform -chdir=terraform destroy
```

After destruction, verify that Terraform manages no remaining resources:

```bash
terraform -chdir=terraform state list
```

## Author

Austin Bishop
U.S. Air Force Ground Transportation veteran transitioning logistics, fleet operations, troubleshooting, and mission-readiness experience into cloud engineering and DevOps.
