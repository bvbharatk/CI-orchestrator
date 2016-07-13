require 'json'

config = (JSON.parse(File.read("vm_config")))
nodes_config = config['nodes']
host_ip_forward = config['host_ip_forward']

#setup dnsmasq to offer ips.
#%x(sed  -i 's/^#\(conf-dir=\/etc\/dnsmasq.d\)/\1 /' /etc/dnsmasq.conf )
#nodes_config.each do |node|
  #node_values=node[1]
  #%x( echo "dhcp-host=#{node_values['mac']} , #{node_values['ip']}" >> /etc/dnsmasq.d/ci_config )
#end  

Vagrant.configure("2") do |config|
  #config.vm.network "private_network", :libvirt__forward_mode => 'nat'
  nodes_config.each do |node|
    node_name   = node[0] # name of node
    node_values = node[1] # content of node

    config.vm.define node_name do |config|    
        config.vm.box='centos/7'
        config.vm.provider :libvirt do |domain|
            domain.memory=node_values['memory']
            domain.cpus=node_values['cpus']
            domain.volume_cache='default'
        end
        config.vm.hostname = node_values['hostname']
        #ports = node_values['ports']
        #ports.each do |port|
        #  config.vm.network :forwarded_port,
        #    host:  port['host'],
        #    guest: port['guest'],
        #    host_ip: host_ip_forward,
        #    id:    port['id']
        #end
        config.vm.network :public_network, :dev=>'br0', :mode => 'bridge', :type =>'bridge', :mac => node_values['mac']
        config.vm.provision "shell" do |s|
          s.inline = "sudo /home/vagrant/sync/scripts/configure_network_interface.sh $1 $2 $3 $4 $5"
          s.args = ['eth1', node_values['mac'], node_values['ip'], node_values['netmask'], node_values['gateway'] ]
        end 
        #config.vm.provision "shell", path: "./scripts/install_common_dependencies.py"
        config.vm.provision "shell", path: node_values['script_path']
    end
  end   
end
