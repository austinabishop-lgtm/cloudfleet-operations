# CloudFleet Troubleshooting Log

This document records technical issues encountered while building and deploying the CloudFleet Operations Platform. Each issue includes the problem, investigation, resolution, and lesson learned.

---

## Issue 1: Docker Permission Denied

### Problem

While testing Docker locally from Windows Subsystem for Linux (WSL), the following command failed:

`docker ps`

Error:

`permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`

### Investigation

I checked my Linux group membership using:

`groups`

The `docker` group was not initially associated with my active user session.

### Resolution

The user was added to the Docker group and a new Linux session was started so the updated group membership could take effect.

Docker connectivity was verified using:

`docker ps`

### Lesson Learned

Docker uses a Unix socket to communicate with the Docker daemon. A non-root user needs appropriate permission to access that socket. Linux group membership changes may also require a new login session before they take effect.

---

## Issue 2: Terraform Reported "No Outputs Found"

### Problem

Running:

`terraform output`

from the CloudFleet project root returned:

`Warning: No outputs found`

even though `terraform/outputs.tf` contained output definitions.

### Investigation

The Terraform configuration and state belonged to the `terraform/` directory rather than the project root.

Terraform commands operate against the configuration and state associated with the current working directory.

### Resolution

I changed into the Terraform directory:

`cd terraform`

Then initialized and validated the configuration:

`terraform init`

`terraform validate`

After running Terraform from the correct directory and applying the infrastructure, the outputs became available.

### Lesson Learned

Always verify the current working directory before troubleshooting Terraform configuration or state problems.

---

## Issue 3: Terraform Route Table Query Returned "list index out of range"

### Problem

While troubleshooting EC2 connectivity, an AWS Command Line Interface (AWS CLI) route-table query returned:

`list index out of range`

### Investigation

The query assumed that the filtered result contained an element at index `[0]`.

The subnet did not have the explicit association expected by the original query because it was using the Virtual Private Cloud (VPC) main route table.

### Resolution

Instead of assuming the first result existed, I queried all route tables belonging to the VPC.

The main route table was found and contained:

`0.0.0.0/0 -> Internet Gateway`

This confirmed that the EC2 subnet had a valid route to the internet.

### Lesson Learned

A failed diagnostic command does not automatically mean the infrastructure is broken. The query itself may contain assumptions that do not match the AWS configuration.

---

## Issue 4: SSH Timeout During Ansible Configuration

### Problem

During an Ansible playbook run, execution progressed through:

- Gathering Facts
- Updating the apt package cache
- Installing Docker

The terminal then appeared to stall.

New Secure Shell (SSH) connections to the EC2 instance returned:

`ssh: connect to host 44.199.192.153 port 22: Connection timed out`

Ansible later reported the host as:

`UNREACHABLE`

### Investigation

Instead of immediately rebooting or recreating the EC2 instance, I tested each infrastructure layer.

#### EC2 Health

AWS CLI status checks showed:

- Instance state: running
- System status: ok
- Instance status: ok

This indicated that both the EC2 instance and underlying AWS infrastructure were healthy.

#### Security Group

The CloudFleet security group allowed:

- TCP port 22 for SSH
- TCP port 5000 for the CloudFleet application

This ruled out the security group as the immediate cause.

#### Public and Private Addressing

The EC2 instance retained:

- Public IPv4 address: 44.199.192.153
- Private IPv4 address: 172.31.8.88

#### Route Table

The VPC main route table contained:

`0.0.0.0/0 -> Internet Gateway`

This confirmed a valid public internet route.

#### Network Access Control List

The Network Access Control List (NACL) allowed inbound and outbound traffic before the default deny rule.

This ruled out the NACL as the cause.

#### Port 22 Connectivity

Netcat was used to test the SSH port:

`nc -vz -w 5 44.199.192.153 22`

At times, TCP port 22 responded successfully even though full SSH sessions continued to experience intermittent timeouts.

---

## Issue 5: Verified Server Health with EC2 Instance Connect

### Problem

Local SSH access remained unreliable even though AWS networking appeared correct.

### Investigation

Amazon EC2 Instance Connect was used as an alternative administrative access method.

The server was successfully accessed through the AWS console.

System health was checked using:

`uptime`

`free -h`

The EC2 instance had low CPU load and sufficient available memory.

The SSH service was checked using:

`sudo systemctl status ssh --no-pager`

Result:

`active (running)`

Docker was checked using:

`sudo systemctl status docker --no-pager`

Result:

`active (running)`

Package activity was checked using:

`ps aux | grep -E "apt|dpkg"`

No active package installation remained.

### Conclusion

The EC2 operating system, SSH service, Docker service, and AWS infrastructure were healthy.

The original Ansible Docker installation had successfully completed despite the interrupted local connection.

### Lesson Learned

Alternative management paths such as EC2 Instance Connect are valuable when normal SSH access becomes unreliable.

---

## Issue 6: Isolating Windows vs WSL Networking

### Problem

SSH from WSL continued to experience intermittent connection timeouts.

### Investigation

Windows PowerShell was used to test TCP port 22 directly:

`Test-NetConnection 44.199.192.153 -Port 22`

Result:

`TcpTestSucceeded : True`

Windows could successfully reach the EC2 SSH port while SSH from WSL was unreliable.

### Conclusion

This significantly reduced the likelihood of an AWS infrastructure problem and shifted troubleshooting toward the local WSL/network path.

WSL was restarted using:

`wsl --shutdown`

Connectivity was then tested again.

### Lesson Learned

When using WSL, Windows and the Linux environment can have different networking behavior. Comparing connectivity from both environments can help isolate local networking problems.

---

## Issue 7: SSH IPQoS Connectivity Resolution

### Problem

Even after verifying AWS infrastructure and restarting WSL, normal SSH connections continued to intermittently time out.

Verbose SSH troubleshooting was performed using:

`ssh -vvv -o ConnectTimeout=10 -i ~/.ssh/cloudfleet-key ubuntu@44.199.192.153`

The connection sometimes timed out before the SSH authentication process began.

### Resolution

SSH was tested with IP Quality of Service (IPQoS) disabled:

`ssh -o IPQoS=none -o ConnectTimeout=10 -i ~/.ssh/cloudfleet-key ubuntu@44.199.192.153`

The connection succeeded.

A local SSH configuration was then created so the option did not need to be entered manually each time.

Example:

`Host cloudfleet`

`HostName 44.199.192.153`

`User ubuntu`

`IdentityFile ~/.ssh/cloudfleet-key`

`IPQoS none`

`ConnectTimeout 10`

SSH could then be initiated using:

`ssh cloudfleet`

### Lesson Learned

The failure was not caused by the EC2 instance, SSH key, security group, route table, or NACL. Systematic testing isolated the problem to SSH client/network-path behavior.

---

## Issue 8: Security Hardening During Troubleshooting

### Problem

The original Terraform security group allowed SSH using:

`0.0.0.0/0`

SSH logs showed unsolicited connection attempts from unrelated public IP addresses.

### Resolution

My current public IPv4 address was identified and the Terraform security group was changed from:

`0.0.0.0/0`

to a single-address `/32` CIDR rule.

Terraform showed:

`Plan: 0 to add, 1 to change, 0 to destroy`

The existing security group was updated without destroying the EC2 instance.

### Lesson Learned

Administrative services such as SSH should not normally be exposed to the entire internet. Infrastructure as Code (IaC) makes security changes reviewable and repeatable.

---

## Issue 9: Restoring Ansible Connectivity

### Problem

Normal SSH worked after applying the IPQoS workaround, but Ansible initially continued using its original SSH behavior.

### Resolution

The Ansible inventory was updated with SSH arguments that included:

`-o IPQoS=none`

Ansible connectivity was tested using:

`ansible cloudfleet -i ansible/inventory.ini -m ping`

Result:

`SUCCESS`

`"ping": "pong"`

The full playbook was then executed successfully.

Final result:

- unreachable=0
- failed=0

### Lesson Learned

Automation tools may use SSH underneath the application layer. When the underlying transport requires a configuration change, the automation configuration may need the same setting.

---

## Issue 10: Editing the Ansible Inventory from the Wrong Server

### Problem

While attempting to edit:

`ansible/inventory.ini`

Nano returned:

`Error writing ansible/inventory.ini: No such file or directory`

### Investigation

I checked:

`pwd`

and:

`whoami`

The results showed:

`/home/ubuntu`

and:

`ubuntu`

This revealed that I was still logged into the EC2 server rather than my local WSL environment.

### Resolution

I exited the EC2 SSH session:

`exit`

Then returned to:

`/home/austin/cloudfleet-operations`

and edited the Ansible inventory successfully.

### Lesson Learned

Before modifying project files, verify which machine and directory the terminal session is currently using.

Useful commands include:

`whoami`

`hostname`

`pwd`

---

## Issue 11: Accidental Combined Terminal Commands

### Problem

Two commands were accidentally pasted together, producing:

`nc: port number invalid: 22cd`

### Cause

The end of the Netcat command and the beginning of the `cd` command were combined into one string.

### Resolution

The commands were rerun separately.

The corrected Netcat command successfully reached TCP port 22.

### Lesson Learned

Terminal errors are not always infrastructure problems. Carefully read the command and error message before changing cloud resources.

---

# Troubleshooting Method Used

The CloudFleet project reinforced a structured troubleshooting approach:

1. Read the exact error.
2. Identify which layer may be failing.
3. Test the simplest explanation first.
4. Verify infrastructure health before changing resources.
5. Test networking layer by layer.
6. Compare alternate access paths when available.
7. Change one variable at a time.
8. Verify the fix.
9. Document the root cause and resolution.
10. Improve security or automation when the troubleshooting process reveals a weakness.

---

# Interview Summary

One of the strongest troubleshooting examples from this project involved intermittent SSH failures during Ansible configuration.

Rather than immediately recreating the EC2 instance, I validated EC2 health checks, security group rules, the public IP address, VPC routing, the Internet Gateway, NACL rules, TCP port 22 connectivity, SSH and Docker service health, Windows connectivity, and WSL networking.

EC2 Instance Connect confirmed that the server itself remained healthy. Further SSH testing showed that disabling IPQoS restored reliable connectivity. I then incorporated the working SSH option into Ansible and successfully restored automated configuration management.

The experience demonstrated systematic cloud troubleshooting across application, operating system, networking, automation, and AWS infrastructure layers.
---

## Issue 12: AWS CLI CloudWatch Command Failed

### Problem

While creating the CloudFleet CPU alarm with the AWS Command Line Interface (AWS CLI), the command failed with:

`badly formed help string`

The CloudWatch alarm was not created.

### Investigation

I verified the AWS CLI versions in both Windows Subsystem for Linux (WSL) and Windows PowerShell.

Both environments reported Python 3.14.4.

The CloudWatch command syntax was reviewed, and the failure appeared to occur locally in the AWS CLI rather than being returned by the CloudWatch service.

### Resolution

Instead of modifying the CloudWatch configuration or risking unnecessary infrastructure changes, I used the AWS Management Console to create the alarm.

The alarm was configured with:

- Metric: CPUUtilization
- Resource: CloudFleet EC2 instance
- Statistic: Average
- Period: 5 minutes
- Threshold: Greater than 70%
- Alarm name: CloudFleet-High-CPU

CloudWatch initially reported `Insufficient data` while collecting enough metric information.

The alarm subsequently transitioned to:

`OK`

This confirmed that CloudWatch was successfully monitoring the EC2 instance and that CPU utilization remained below the configured threshold.

### Lesson Learned

When a cloud-management command fails, determine whether the error originates from the local tooling or from the cloud service itself before changing infrastructure.

Alternative management interfaces, such as the AWS Management Console, can provide a safe way to continue while a local tooling problem is investigated.
---

## Issue 13: SSH Rule Did Not Match the Current Public IP Address

### Problem

SSH connections to the EC2 instance timed out even though the instance was running and both AWS status checks reported `ok`.

### Evidence

The administrator's current public IPv4 address was compared with the `/32` address in `terraform/security.tf`.

The two addresses did not match. Therefore, the security group correctly rejected the connection before SSH authentication could begin.

### Root Cause

The administrator's internet egress address had changed, but the Terraform security-group rule still allowed the previous address.

### Resolution

The SSH ingress rule was updated to the current public IPv4 `/32` address. Terraform displayed an in-place security-group update with no EC2 replacement.

### Verification

SSH progressed from a connection timeout to a successful connection and public-key authentication.

### Lesson Learned

When SSH is restricted to a `/32` address, verify the current egress address before investigating the server. A healthy EC2 instance can still be unreachable when the client address does not match the security-group rule.

---

## Issue 14: VPN and Cellular Networking Changed the Egress Address

### Problem

The public IPv4 address changed multiple times during SSH troubleshooting. A rule that matched moments earlier could stop matching.

### Evidence

Repeated requests to an external address-checking service returned different addresses while a Virtual Private Network (VPN) and cellular connection were active.

### Root Cause

VPN routing and cellular tethering changed the public egress path used by the laptop. The security group was restricted to a different `/32` address.

### Resolution

The connection path was stabilized, the active public address was verified repeatedly, and the security-group rule was aligned with that address.

### Verification

After the address remained stable and matched Terraform, SSH reached the server successfully.

### Lesson Learned

A restricted administrative rule improves security but creates an operational dependency on the administrator's current public address. VPNs, mobile networks, and Internet Service Provider changes must be considered during connectivity troubleshooting.

---

## Issue 15: Stale SSH Alias and Ansible Inventory

### Problem

The EC2 instance had a new public address, but the local SSH alias and Ansible inventory still referenced an older instance address.

### Evidence

The effective SSH configuration was inspected with:

`ssh -G cloudfleet`

The Ansible inventory was also printed and compared with the current Terraform output.

### Root Cause

Infrastructure values had changed without being updated in local client configuration.

### Resolution

The `HostName` entry in `~/.ssh/config` and the CloudFleet host in `ansible/inventory.ini` were updated to the current address.

### Verification

The `ssh cloudfleet` alias connected to the correct instance, and the Ansible ping module returned `pong`.

### Lesson Learned

After infrastructure changes, verify every downstream consumer of an address or identifier. Terraform output, SSH configuration, and automation inventory must remain synchronized.
---

## Issue 16: Ansible Check Mode Could Not Find the Docker Package

### Problem

The Ansible playbook was executed with `--check --diff` before the real deployment.

The package installation task failed with:

`No package matching 'docker.io' is available`

### Evidence

The preceding package-cache task reported that it would change the host. However, check mode simulates changes and does not necessarily perform every required action.

### Root Cause

The Ubuntu package cache needed to be refreshed before Ansible could locate `docker.io`. Check mode predicted the cache update without completing the update required by the following task.

### Resolution

The playbook was executed normally so the package cache could actually be updated and Docker could be installed.

### Verification

The real playbook run installed Docker successfully and completed with `failed=0`.

### Lesson Learned

Ansible check mode is useful for previewing changes, but it cannot always simulate dependencies between tasks. A later task may depend on a change that check mode did not actually perform.

---

## Issue 17: Docker Service Was Missing During Ansible Check Mode

### Problem

After package metadata became available, check mode predicted that Docker would be installed but then failed while managing the Docker service:

`Could not find the requested service docker`

### Evidence

The package task showed that `docker.io` and its dependencies would be installed. The following service task could not find Docker on the host.

### Root Cause

Check mode simulated the Docker installation without creating the actual service. The service-management task therefore searched for a service that did not yet exist.

### Resolution

The playbook was run without `--check`, allowing Docker to be installed before the service task executed.

### Verification

The Docker service reported both:

* `active`
* `enabled`

A second Ansible playbook run completed with `changed=0`, proving the resulting configuration was idempotent.

### Lesson Learned

Dry-run results must be interpreted in context. Check mode can produce false failures when one simulated task creates a package, file, account, or service required by a later task.

---

## Issue 18: Flask Development Server Exposed Debug Mode

### Problem

The first deployed container used Flask's built-in development server with debug mode enabled.

Container logs displayed:

* A warning that the server was not intended for production
* `Debugger is active`
* A debugger personal identification number

### Risk

The Flask development server is not designed for a public production workload. Debug mode can expose sensitive application details and unsafe debugging capabilities.

### Root Cause

The application started with:

`app.run(host="0.0.0.0", port=5000, debug=True)`

The Docker image also started the application directly with Python.

### Resolution

Debug mode was disabled. Gunicorn was added as a pinned dependency, and the Docker startup command was changed to run two workers with two threads.

### Verification

The public endpoint continued returning `HTTP/1.1 200 OK`. Its server header changed from Werkzeug to Gunicorn, and container logs showed Gunicorn workers starting successfully.

### Lesson Learned

A successful HTTP response does not prove that an application is deployed securely. Runtime configuration, server type, debug settings, and logs must also be reviewed.
---

## Issue 19: Local Python Could Not Import Flask

### Problem

The application passed Python syntax compilation, but a local health-route test failed with:

`ModuleNotFoundError: No module named 'flask'`

### Evidence

The test was executed with the system `python3` interpreter. The project already contained an ignored virtual environment under `venv/`.

### Root Cause

Flask was installed inside the project virtual environment but not in the system-wide Python environment.

### Resolution

The pinned application dependencies were installed with the virtual-environment interpreter:

`./venv/bin/python -m pip install -r app/requirements.txt`

The health-route test was then executed with:

`./venv/bin/python`

### Verification

The Flask test client returned status code `200` and the expected healthy JSON response.

### Lesson Learned

Python dependencies belong in an isolated project environment. Verify which interpreter is running before concluding that an application dependency is missing.

---

## Issue 20: AWS CLI Pager Output Created Accidental Files

### Problem

Two unexpected untracked files appeared in the repository:

* `cloudwatch describe-alarms \`
* `tate list`

### Evidence

`git status` identified the files. Their exact escaped names and sizes were inspected before deletion.

The contents contained CloudWatch table output and pager help text rather than project source code.

### Root Cause

Commands and pager output were accidentally redirected or pasted in a way that created files with fragments of command names.

### Resolution

The files were inspected to confirm that they did not contain required project work. They were then removed using their exact quoted filenames.

AWS CLI commands were subsequently run with:

`AWS_PAGER=""`

This disabled interactive paging for those commands.

### Verification

`git status` returned a clean working tree after the accidental files were removed.

### Lesson Learned

Do not delete unfamiliar files immediately. Inspect their names, sizes, and contents first. Disable command paging when automation or terminal behavior makes output difficult to control.

---

## Issue 21: AWS CLI SNS Publish Failed on Python 3.14

### Problem

A controlled Amazon Simple Notification Service (Amazon SNS) test could not be published with the AWS Command Line Interface (AWS CLI).

Even a simplified `aws sns publish` command failed locally with:

`badly formed help string`

### Evidence

The SNS topic existed, the email subscription was confirmed, and both CloudWatch alarms referenced the correct topic Amazon Resource Name (ARN). The error occurred before the request reached the SNS service.

The local environment used AWS CLI version 2.31.35 with Python 3.14.

### Root Cause

The failure was caused by a local AWS CLI compatibility problem involving stricter argument-parser behavior in Python 3.14. It was not an SNS topic, subscription, permission, or CloudWatch configuration failure.

### Resolution

A command-line workaround used the AWS Software Development Kit (SDK) for Python, known as Boto3, from the ignored local virtual environment.

The script discovered the CloudFleet topic and called the SNS publish operation directly.

### Verification

The publish operation returned success, and the controlled test notification arrived at the confirmed email address.

### Lesson Learned

Separate local tooling failures from cloud-service failures. When one management interface fails, use verified state and a safe alternative client rather than changing healthy infrastructure.

---

# Final Troubleshooting Principles

The CloudFleet incidents reinforced the following engineering practices:

1. Read and preserve the exact error message.
2. Identify whether the failure is local, network-related, operating-system-related, application-related, automation-related, or cloud-related.
3. Verify system health before replacing resources.
4. Compare declared configuration with live state.
5. Test one hypothesis at a time.
6. Use alternate access paths to isolate the affected layer.
7. Understand the limits of dry-run and check modes.
8. Inspect files and command output before deleting anything.
9. Apply the smallest safe correction.
10. Retest the original failure after making a change.
11. Verify repeatability and idempotency.
12. Record the root cause, resolution, evidence, and lesson learned.
