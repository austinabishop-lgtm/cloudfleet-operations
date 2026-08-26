# CloudFleet Interview Guide

## 30-Second Project Explanation

CloudFleet is an end-to-end cloud engineering project inspired by my U.S. Air Force Ground Transportation experience. I standardized vehicle and mission data, built a Python Flask readiness dashboard, containerized it with Docker, provisioned Amazon Web Services infrastructure with Terraform, automated deployment with Ansible, and added Amazon CloudWatch monitoring with Amazon Simple Notification Service email alerts. I also documented 21 troubleshooting incidents to demonstrate how I diagnose problems across application, Linux, networking, automation, and cloud layers.

## 90-Second Project Explanation

CloudFleet Operations Platform connects my transportation and logistics background with cloud engineering.

The business problem was that fleet, dispatch, and maintenance information can arrive in inconsistent formats, making operational visibility and automation unreliable. I created standardized JavaScript Object Notation data models for vehicles and missions and built a Python Flask dashboard that displays vehicle availability, maintenance status, mission assignments, and operational alerts.

I packaged the application with Docker and replaced Flask's development server with Gunicorn for a safer deployed runtime. Terraform provisions the Amazon Elastic Compute Cloud instance, security group, SSH key-pair registration, CloudWatch alarms, operations dashboard, Amazon Simple Notification Service topic, and email subscription. Ansible installs Docker, copies the application, conditionally rebuilds the image, manages the container, and verifies a dedicated health endpoint.

I validated the environment through HTTP checks, Docker inspection, Ansible idempotency, Terraform drift detection, CloudWatch alarm states, dashboard metrics, and a controlled email-notification test. The strongest part of the project was troubleshooting real failures systematically instead of rebuilding resources without evidence.

## Architecture Explanation

The system has five major layers:

1. **Data layer:** Standardized vehicle and mission records stored as JavaScript Object Notation (JSON).
2. **Application layer:** Python and Flask calculate fleet-readiness metrics and render the dashboard.
3. **Runtime layer:** Docker packages the application, while Gunicorn serves it through multiple workers.
4. **Infrastructure and automation layer:** Terraform provisions AWS resources, and Ansible configures the server and deploys the container.
5. **Operations layer:** Amazon CloudWatch collects metrics and evaluates alarms, while Amazon Simple Notification Service (Amazon SNS) delivers incident and recovery emails.

## Why Each Tool Was Used

### Why Terraform?

Terraform provides Infrastructure as Code (IaC). It makes infrastructure repeatable, reviewable, version-controlled, and easier to destroy safely.

### Why Ansible?

Terraform creates infrastructure, while Ansible configures the operating system and deploys the workload. Ansible was used for package installation, Docker management, file transfer, image builds, container lifecycle management, and health verification.

### Why Docker?

Docker packages the application and dependencies into a consistent runtime. This reduces differences between local and cloud environments.

### Why Gunicorn?

Flask's built-in server is intended for development. Gunicorn provides a production-oriented Web Server Gateway Interface (WSGI) runtime with configurable workers, threads, and timeouts.

### Why CloudWatch?

Amazon CloudWatch provides native AWS metrics, dashboards, and alarms. It allowed the project to monitor processor utilization, instance health, and network traffic proactively.

### Why Amazon SNS?

Amazon SNS decouples alarm detection from message delivery. CloudWatch publishes a state change to the topic, and the confirmed email subscription receives the notification.

## Infrastructure as Code Versus Configuration Management

Terraform and Ansible solve different problems.

Terraform manages cloud resources such as the EC2 instance, security group, CloudWatch alarms, dashboard, and SNS topic.

Ansible manages configuration inside the server, such as installing Docker, copying files, building the image, starting the container, and checking application health.

A concise interview response is:

> Terraform creates and manages the infrastructure; Ansible configures the server and deploys the application running on that infrastructure.

## Idempotency

Idempotency means an automation tool can run repeatedly without making unnecessary changes after the desired state has been reached.

The second CloudFleet Ansible run completed with:

* `changed=0`
* `unreachable=0`
* `failed=0`

Terraform also reported no changes after comparing the configuration with the deployed environment.

These results demonstrated idempotency and lack of configuration drift.

## Health Checks Versus Monitoring

A health check answers:

> Is the service responding correctly right now?

CloudFleet's `/health` route returns an HTTP `200` response and healthy JSON.

Monitoring answers:

> How has the system behaved over time, and when should an operator be notified?

CloudWatch tracks processor utilization, status-check failures, and network traffic. Its alarms notify operators through SNS.

Both are required because a process can be running while the application is unhealthy, and a single successful request does not describe long-term behavior.

## Security Explanation

CloudFleet used several security controls:

* SSH public-key authentication instead of passwords
* An ED25519 key pair
* SSH restricted to one administrator IPv4 `/32` address
* Sensitive Terraform variable files excluded from Git
* Terraform state excluded from Git
* Private SSH keys kept outside the repository
* Flask debug mode disabled
* Gunicorn used for the deployed runtime
* Infrastructure changes reviewed through Terraform plans

The application port remained public over HTTP for demonstration. For production, I would add an Application Load Balancer, Transport Layer Security, a managed certificate, a domain name, and tighter network segmentation.

## Monitoring Explanation

CloudFleet includes:

* A high-processor alarm using average `CPUUtilization`
* An EC2 `StatusCheckFailed` alarm using the maximum statistic
* A dashboard for processor utilization, status checks, and network traffic
* SNS incident and recovery actions
* A confirmed email subscription

The alarms initially showed `INSUFFICIENT_DATA`, which is expected while CloudWatch gathers the required datapoints. They later transitioned to `OK`, showing that sufficient data was available and thresholds were not breached.

## Primary STAR Troubleshooting Story

### Situation

During CloudFleet deployment, SSH and Ansible connections to the EC2 instance began timing out.

### Task

I needed to restore secure administrative access without unnecessarily replacing a healthy server or weakening the security group.

### Action

I checked the EC2 state and both AWS status checks, reviewed the security-group rule, compared it with my current public address, verified routing and network controls, tested port 22, used verbose SSH output, and compared alternate network paths.

I discovered that the restricted `/32` rule did not always match because a Virtual Private Network and cellular networking changed my public egress address. I also identified intermittent SSH client behavior that was resolved with `IPQoS none`. I updated the Terraform rule, SSH alias, and Ansible inventory, then retested authentication and automation.

### Result

SSH public-key authentication succeeded, Ansible returned `pong`, and the full deployment completed with zero unreachable or failed hosts. I preserved the restricted SSH rule instead of opening port 22 to the entire internet.

### Lesson

The incident reinforced layered troubleshooting: confirm health, compare expected and actual configuration, isolate the network path, change one variable, and verify the original failure.

## Secondary STAR Story: Production Hardening

### Situation

The deployed application returned HTTP `200 OK`, but its logs showed that Flask debug mode and the development server were active.

### Task

I needed to harden the runtime without breaking deployment automation or application availability.

### Action

I disabled debug mode, pinned Flask and Gunicorn versions, changed the Docker startup command to Gunicorn, and reran the Ansible deployment. The playbook detected the source changes, rebuilt the image, replaced the outdated container, and executed the health check.

### Result

The application continued returning HTTP `200 OK`, the server header changed to Gunicorn, multiple workers started successfully, and a repeated Ansible run completed with `changed=0`.

### Lesson

Availability alone does not prove production readiness. Logs, runtime configuration, repeatability, and security must also be verified.

## Third STAR Story: Monitoring and Notification

### Situation

The application was available, but there was no proactive method to identify infrastructure degradation or notify an operator.

### Task

I needed to add repeatable monitoring, visualization, and email notification without manually configuring resources outside the infrastructure code.

### Action

I created Terraform resources for processor and EC2 status-check alarms, built a CloudWatch dashboard, created an SNS topic and email subscription, connected alarm and recovery actions, and protected the notification email with an ignored sensitive variable.

### Result

Both alarms reached `OK`, the dashboard displayed live metrics, Terraform reported no drift, and a controlled SNS test email arrived successfully.

### Lesson

Monitoring becomes operationally useful when metrics, thresholds, notification paths, verification, and ownership are designed together.

## Common Technical Interview Questions

### What happens when a user opens CloudFleet?

The browser sends an HTTP request to the EC2 public address on port 5000. The security group permits the traffic. Docker maps the host port to the container, Gunicorn receives the request, Flask processes standardized data, and the generated dashboard is returned to the browser.

### What is a security group?

A security group is a stateful virtual firewall attached to an AWS resource. CloudFleet uses one rule for public application traffic and a separate restricted rule for SSH administration.

### What does `/32` mean?

A `/32` Classless Inter-Domain Routing block represents exactly one IPv4 address. It was used to limit SSH access to the administrator's current public address.

### Why did SSH time out instead of rejecting the key?

The security group dropped the connection before SSH authentication. The request never reached the stage where the server could accept or reject the key.

### What is Terraform state?

Terraform state maps declared resources to real infrastructure. It allows Terraform to calculate differences and decide whether to create, update, replace, or destroy resources.

### What is configuration drift?

Configuration drift occurs when deployed infrastructure differs from its declared configuration. A Terraform plan showing no changes confirmed that CloudFleet had no detected drift.

### Why was Terraform state excluded from Git?

State can contain infrastructure identifiers and potentially sensitive values. Local state was excluded to reduce accidental exposure. A team environment should use an encrypted remote backend with locking.

### What does Ansible `changed=0` prove?

It shows that the host already matched the desired configuration and the playbook did not perform unnecessary changes during that run.

### Why can Ansible check mode fail?

Check mode simulates changes. If a later task depends on a package, file, or service that an earlier task only simulated creating, the later task may fail even though a normal run would succeed.

### Why use a dedicated health endpoint?

A dedicated endpoint provides a small, predictable, machine-readable response for automation, monitoring, load balancers, and deployment verification.

### What is the difference between an EC2 system check and instance check?

A system check detects problems with AWS infrastructure supporting the instance. An instance check detects operating-system or network problems inside the virtual machine.

### Why use `treat_missing_data = "notBreaching"`?

It prevents missing metric data from automatically being treated as an alarm condition. The correct choice depends on the workload; for some critical services, missing data should instead be treated as a failure.

### What would you improve for production?

I would add:

* A custom Virtual Private Cloud with public and private subnets
* An Application Load Balancer
* HTTPS with AWS Certificate Manager
* A domain name
* AWS Systems Manager Session Manager instead of public SSH
* Amazon Elastic Container Registry for images
* Continuous integration and continuous deployment
* Remote encrypted Terraform state with locking
* Centralized application logs
* Secrets Manager or Parameter Store
* Automated testing
* High availability across multiple Availability Zones
* Auto Scaling
* Backup and recovery procedures

## Logistics-to-Cloud Connection

My Ground Transportation experience involved:

* Vehicle accountability
* Dispatch coordination
* Mission scheduling
* Operational readiness
* Maintenance awareness
* Personnel and asset coordination
* Troubleshooting under time constraints
* Risk management
* Documentation and handoffs

CloudFleet translates those responsibilities into cloud engineering:

| Logistics Experience      | Cloud Engineering Application         |
| ------------------------- | ------------------------------------- |
| Vehicle accountability    | Infrastructure and asset inventory    |
| Dispatch coordination     | Workload scheduling and deployment    |
| Mission readiness         | Service health and availability       |
| Preventive maintenance    | Monitoring and proactive remediation  |
| Control-center visibility | CloudWatch dashboards                 |
| Incident response         | Structured troubleshooting            |
| Operating procedures      | Infrastructure and configuration code |
| Shift documentation       | Git history and technical runbooks    |

## Résumé Bullets

* Engineered a logistics-focused operations platform on AWS using Terraform, Ansible, Docker, Python, Flask, Gunicorn, Amazon EC2, CloudWatch, and SNS, delivering repeatable deployment, health monitoring, and automated email alerts.
* Automated EC2 provisioning and application deployment with Terraform Infrastructure as Code and idempotent Ansible configuration management, validating zero drift and repeated runs with `changed=0` and `failed=0`.
* Containerized and hardened a Python Flask fleet-readiness dashboard with Docker and Gunicorn, disabled debug mode, pinned dependencies, and verified public and machine-readable health endpoints with HTTP `200 OK`.
* Implemented CloudWatch alarms and an operations dashboard for processor utilization, EC2 status checks, and network traffic, integrating SNS incident and recovery notifications with verified end-to-end email delivery.
* Secured remote administration with ED25519 SSH authentication and a restricted IPv4 `/32` security-group rule while protecting Terraform state, private keys, and environment-specific variables from Git.
* Diagnosed and resolved 21 cloud, Linux, networking, automation, and application incidents through evidence-based troubleshooting, including dynamic VPN addressing, SSH transport behavior, Ansible check-mode limitations, and AWS CLI compatibility.

## LinkedIn Project Description

Built CloudFleet Operations Platform, an end-to-end AWS and DevOps portfolio project inspired by U.S. Air Force Ground Transportation operations. Standardized fleet and mission data with JSON, developed a Python Flask readiness dashboard, containerized it with Docker and Gunicorn, provisioned AWS infrastructure with Terraform, automated deployment with Ansible, implemented CloudWatch dashboards and alarms, and integrated Amazon SNS email notifications. Verified application health, infrastructure idempotency, configuration drift, monitoring state, and end-to-end alert delivery while documenting 21 real troubleshooting scenarios.

## Final Interview Message

CloudFleet shows that I can do more than launch an EC2 instance. I can connect a business problem to a technical design, automate infrastructure and configuration, deploy and harden an application, monitor its health, notify operators, troubleshoot failures systematically, document the work, and manage cloud resources with security and cost in mind.
