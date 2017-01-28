# create network spacename
ip netns add entrystats

# create a pair of virtual network interfaces (veth-a and veth-b):
ip link add entryeth0 type veth

# change the active namespace of the veth-a interface:
ip link set entryeth0 netns entrystats

# configure the IP addresses of the virtual interfaces:
ip netns exec entrystats ifconfig entryeth0 up 192.168.160.1 netmask 255.255.255.0

# configure the routing in the test namespace:
ip netns exec entrystats route add default gw 192.168.160.254 dev entryeth0

# activate ip_forward and establish a NAT rule to forward the traffic coming in from the namespace you created (you have to adjust the network interface and SNAT ip address):
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -s 192.168.160.0/24 -o YOURNETWORKINTERFACE -j SNAT --to-source YOURIPADDRESS

# finally, you can run the process you want to analyze in the new namespace, and wireshark too:
# ip netns exec entrystats thebinarytotest
