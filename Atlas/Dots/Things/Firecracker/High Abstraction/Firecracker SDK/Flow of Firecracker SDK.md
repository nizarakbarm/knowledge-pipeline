Step in creating instance with SDK:
1. Install Golang
```bash
zypper install -y go go-doc
```
Add this to .bashrc:
```bash
export PATH=$PATH:/root/go/bin
```
1. configure the machine -> using type struct Config
	- set socket path
	- set kernel image path
	- set kernel args
	- set drives:
		- drive id
		- root file system path on PathOnHost
		- isRootDevice true
		- isReadOnly true
	- Set network interfaces
		- mac address
		- host device name (tap0)
	- Machine Configuration
		- VCPU Count
		- Memory Size in Mib
	- Forward Signal
	- Log level
	- Log path
	- metrics path
2. Validate config and network 
3. Create firecracker stdout and stderr at temporary dir
4. Set VMCommandBuilder for setting exec.Cmd for starting firecracker
5. Installing CNI
	1. `wget https://github.com/containernetworking/plugins/releases/download/v1.8.0/cni-plugins-linux-amd64-v1.8.0.tgz`
	2. `mkdir -p /opt/cni/plugin`
	3. `tar -C /opt/cni/bin -xzf cni-plugins-linux-amd64-v1.8.0.tgz`
	4. inside `/opt/cni/bin`:
	```Bash
	total 96092
	drwxr-xr-x 2 root root      291 Sep  1 15:29 .
	drwxr-xr-x 3 root root       17 Nov  4 13:36 ..
	-rwxr-xr-x 1 root root  5042186 Sep  1 15:29 bandwidth
	-rwxr-xr-x 1 root root  5694189 Sep  1 15:29 bridge
	-rwxr-xr-x 1 root root 13719696 Sep  1 15:29 dhcp
	-rwxr-xr-x 1 root root  5251247 Sep  1 15:29 dummy
	-rwxr-xr-x 1 root root  5701763 Sep  1 15:29 firewall
	-rwxr-xr-x 1 root root  5159307 Sep  1 15:29 host-device
	-rwxr-xr-x 1 root root  4350430 Sep  1 15:29 host-local
	-rwxr-xr-x 1 root root  5273398 Sep  1 15:29 ipvlan
	-rw-r--r-- 1 root root    11357 Sep  1 15:29 LICENSE
	-rwxr-xr-x 1 root root  4301450 Sep  1 15:29 loopback
	-rwxr-xr-x 1 root root  5306499 Sep  1 15:29 macvlan
	-rwxr-xr-x 1 root root  5107586 Sep  1 15:29 portmap
	-rwxr-xr-x 1 root root  5474778 Sep  1 15:29 ptp
	-rw-r--r-- 1 root root     2343 Sep  1 15:29 README.md
	-rwxr-xr-x 1 root root  4521078 Sep  1 15:29 sbr
	-rwxr-xr-x 1 root root  3772408 Sep  1 15:29 static
	-rwxr-xr-x 1 root root  5330851 Sep  1 15:29 tap
	-rwxr-xr-x 1 root root  4384728 Sep  1 15:29 tuning
	-rwxr-xr-x 1 root root  5266939 Sep  1 15:29 vlan
	-rwxr-xr-x 1 root root  4684912 Sep  1 15:29 vrf
	```
	5. Install tc-redirect-tap
	```bash
mkdir -p $GOPATH/src/github.com/awslabs/tc-redirect-tap
cd $GOPATH/src/github.com/awslabs/tc-redirect-tap
git clone https://github.com/awslabs/tc-redirect-tap.git .
make install
	```