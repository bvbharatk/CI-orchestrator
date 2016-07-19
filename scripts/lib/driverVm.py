#!/usr/bin/python
import os
import sys
import json
from inspect import getsourcefile

currentDir=os.path.dirname(os.path.abspath(getsourcefile(lambda _:0)))
sys.path.append(os.path.join(currentDir,"lib"))

import logging
from bashUtils import bash
from cobbler_setting import settings as cobblerSettings
from puppet_agent_conf import agent_conf as puppetAgentConf
from cobbler_dhcp_config import dhcp_template as dhcpConf
from cobbler_named_config import named_template as namedConf

logging.basicConfig(format='%(asctime)s %(levelname)s  %(name)s %(lineno)d  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

class driverVm:
      def __init__(self):
          self.logger=logging.getLogger("driverVM")
          self.ci_git_url="https://github.com/bvbharatk/cloudstack-automation.git"
          self.config=self.loadJson(os.path.join(os.sep.join(currentDir.split(os.sep)[:-2]),"vm_config"))
          ##loading ci host config
          self.ci_config=self.loadJson(os.path.join(os.sep.join(currentDir.split(os.sep)[:-2]),"ci_config"))
 
      def loadJson(self,filePath):
          f=open(filePath,'r')
          content=f.read()
          f.close()
          return json.loads(content)

      def checkForSuccess(self, bashObj):
          if (not bashObj.isSuccess()):
              raise Exception("Failed to execute commmand %s, Error message %s"%(bashObj.args,bashObj.getErrMsg()))

      def installCobbler(self):
          self.logger.info("begining cobbler install")
          self.checkForSuccess(bash("yum -y install cobbler cobbler-web dhcp bind xinetd selinux-policy-devel syslinux pykickstart"))
          self.checkForSuccess(bash("semanage permissive -a cobblerd_t"))
          self.checkForSuccess(bash("sed -i 's~disable.*~disable                 = no~' /etc/xinetd.d/tftp"))
          self.checkForSuccess(bash("systemctl enable xinetd && systemctl enable rsyncd"))
          self.checkForSuccess(bash("systemctl enable cobblerd && systemctl start cobblerd"))
          self.checkForSuccess(bash("systemctl start xinetd && systemctl start rsyncd")) 
          bash("ln -s '/usr/lib/systemd/system/httpd.service' '/etc/systemd/system/multi-user.target.wants/httpd.service")
          self.checkForSuccess(bash("systemctl enable httpd && systemctl start httpd"))
          self.checkForSuccess(bash("systemctl restart cobblerd"))
          self.logger.info("Cobbler install complete")
      
      def installPuppet(self):
          self.logger.info("Begining puppet install")
          self.logger.info("Adding puppet labs collection repository")
          self.checkForSuccess(bash("rpm -ivh https://yum.puppetlabs.com/puppetlabs-release-pc1-el-7.noarch.rpm")) 
          self.checkForSuccess(bash("yum -y install puppetserver"))
          self.checkForSuccess(bash("systemctl enable puppetserver && systemctl start puppetserver"))
          self.logger.info("puppet install complete")

      def setupCobbler(self):
          settings=cobblerSettings()
          settings.driver_vm_ip=self.config['nodes']['driverVM']['ip']
          settings.driver_vm_hostname=self.config['nodes']['driverVM']['hostname']
          settings.puppet_version='3'
          settings.forward_zone=".".join(self.config['nodes']['driverVM']['hostname'].split(".")[1:])
          settings.reverse_zone=".".join(self.config['nodes']['driverVM']['ip'].split(".")[:-1])
          f=open("/etc/cobbler/settings",'w')
          print >> f, settings
          f.close()
          self.logger.info("configuring cobbler dhcpd tempalte")
          dhcp_conf=dhcpConf()
          dhcp_conf.subnet=".".join(self.config['nodes']['driverVM']['ip'].split(".")[:3])+".0"
          dhcp_conf.netmask=self.config['nodes']['driverVM']['netmask']
          dhcp_conf.driver_vm_gateway=self.config['nodes']['driverVM']['gateway']
          dhcp_conf.driver_vm_ip=self.config['nodes']['driverVM']['ip']
          dhcp_conf.domain="*."+".".join(self.config['nodes']['driverVM']['hostname'].split(".")[1:])
          f=open('/etc/cobbler/dhcpd.template', 'w')
          print >> f, dhcp_conf
          f.close()
          self.logger.info("configuring cobbler named template")
          named_conf=namedConf()
          named_conf.driver_vm_ip=self.config['nodes']['driverVM']['ip']
          named_conf.dns=self.config['dns']
          f=open('/etc/cobbler/named.template','w')
          print >> f, named_conf
          f.close() 

      def  setupPuppet(self):
           conf=puppetAgentConf()
           self.logger.info("backup the original files to /etc/puppet/backup")
           bash("mkdir -p /etc/puppet/backup")
           bash("mv *.conf /etc/puppet/backup/")
           nameString="*."+".".join(self.config['nodes']['driverVM']['hostname'].split(".")[1:])
           conf.search=nameString 
           conf.driver_vm_hostname=self.config['nodes']['driverVM']['hostname']
           f=open("/etc/puppet/agent.conf",'w')
           print >> f, conf
           f.close()
           cmd="echo %s >> /etc/puppet/autosign.conf"%nameString
           self.checkForSuccess(bash(cmd))
           self.checkForSuccess(bash("cp -f %s/puppet/* /etc/puppet/."%currentDir)) 
      
      def installCI(self):
          self.checkForSuccess(bash("mkdir -p /automation/jenkins"))
          self.logger.info("installing CI dependencies")
          self.checkForSuccess(bash("wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm"))
          self.checkForSuccess(bash("rpm -ivh mysql-community-release-el7-5.noarch.rpm"))
          self.checkForSuccess(bash("yum install -y mysql-server"))
          self.checkForSuccess(bash("yum install -y mysql-devel"))
          self.checkForSuccess(bash("systemctl enable mysqld && service mysqld start"))
          self.checkForSuccess(bash("pip install -r %s"%(os.path.join(currentDir,"ci_requirements.txt"))))
          self.checkForSuccess(bash("mkdir -p /root/cloud-autodeploy/"))
          self.checkForSuccess(bash("sh %s"%(os.path.join(currentDir, "install_nfs.sh")))) 
          self.checkForSuccess(bash("mkdir -p /automation/jenkins"))
          self.checkForSuccess(bash("yum install -y git"))
          os.chdir("/root/cloud-autodeploy")
          self.checkForSuccess(bash("git clone %s"%(self.ci_git_url)))
       
      def runConfigurator(self):
          self.checkForSuccess(bash("python %s"%(os.path.join(currentDir,"configure_driverVM.py"))))
     
if __name__=='__main__':
   driverVM=driverVm()
   driverVM.installCobbler()
   driverVM.setupCobbler()
   driverVM.installPuppet()
   driverVM.setupPuppet()
   driverVM.installCI()
   driverVM.runConfigurator()
