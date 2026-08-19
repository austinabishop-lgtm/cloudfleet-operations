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
