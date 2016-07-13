#!/usr/bin/python
import os
import sys
import json
from inspect import getsourcefile
import MySQLdb

currentDir=os.path.dirname(os.path.abspath(getsourcefile(lambda _:0)))
sys.path.append(os.path.join(currentDir,"lib"))

import logging
from bashUtils import bash

logging.basicConfig(format='%(asctime)s %(levelname)s  %(name)s %(lineno)d  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

class driverVmConfigurator:
      def __init__(self):
          self.logger=logging.getLogger("driverVmConfigurator")
          self.ci_git_url="https://github.com/bvbharatk/cloudstack-automation.git"
          self.config=self.loadJson(os.path.join(os.sep.join(currentDir.split(os.sep)[:-2]),"vm_config"))
          ##loading ci host config
          self.ci_config=self.loadJson(os.path.join(os.sep.join(currentDir.split(os.sep)[:-2]),"ci_config"))
          self.dbHost="localhost"
          self.username="root"
          self.passwd=""
          self.database="resource_db"

      def loadJson(self,filePath):
          f=open(ConfigFilePath,'r')
          content=f.read()
          f.close()
          return json.loads(content)

      def checkForSuccess(self, bashObj):
          if (not bashObj.isSuccess()):
              raise Exception("Failed to execute commmand %s, Error message %s"%(bashObj.args,bashObj.getErrMsg()))
      
      def downLoadTonfs(self, url):
          self.checkForSuccess(bash("ssh vagrant@%s 'wget -O /var/exports/iso/ %s'"%(self.config['nodes']['nfsVM']['ip'], url)))
     
      def importDistroFromMountPt(self, mounturl):
          self.checkForSuccess(bash("mount -t nfs %s %s"%(mounturl.replace("nfs://",""), "/media")))
          self.checkForSuccess(bash("cobbler distro import --name=CentosDef --path=/media"))
      
      def cobblerAddReposToProfiles(self, repolist):
          result=bash("cobbler profile list")
          if result.stdout!=None:
             for profile in result.split('\n'):
                 bash("cobbler profile edit --name=%s --repos='%s'"%(profile, " ".join(repolist)))
       
      def cobblerAddRepos(self):
          for repo in self.ci_config['repos'].keys():
              self.checkForSuccess(bash("cobbler repo add --name=%s --mirror=%s --mirror-locally=N"%(repo, self.ci_config[repo]['url'])))
  
      def configureCobbler(self):
          self.logger.info("configuring cobbler")
          self.logger.info("importing distros and creating profiles")
          if len(self.ci_config['centosImage']['download_url']) > 0:
                self.downLoadTonfs(self.ci_config['centosImage']['download_url'])
                mounturl="nfs://%s:/var/export/iso/%s"%(self.config['nodes']['nfsVM']['ip'], "/".join(self.ci_config['centosImage']['download_url'].split("/")[-2:]))       
          else:
              mounturl=self.ci_config['centosImage']['mount_url']
          self.importDistroFromMountPt(mounturl)
          self.cobblerAddRepos()
          self.cobblerAddReposToProfiles(self.ci_config['repos'].keys())
          self.checkForSuccess(bash("cobbler sync"))
     
      def importDatabase(self):
          self.checkForSuccess("mysql -u root < %s/CI_db.sql"%(currentDir))

      def populateDataBase(self):
          self.logger.info("populating static host info")
          self.logger.info("connecting to db")
          con = MySQLdb.connect(self.dbHost,self.username, self.passwd, self.database) 
          cursor=con.cursor()
          for host in self.ci_config['hosts'].keys():
              h=self.ci_config['hosts'][host]
              cursor.execute("INSERT INTO `resource_db`.`static_host_info` (`id`, `hostname`, `ip`, `netmask`, `gateway`, `mac`, `ipmi_hostname`, `ipmi_password`) Values ('','%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(h['hostname'], h['ip'], h['netmask'], h['gateway'], h['mac'], h['ipmi_hostname'], h['ipmi_password']))
          for template in self.ci_config['systemvm_template'].keys():
              t=self.ci_config['systemvm_templates'][template]
              cursor.execute("INSERT INTO `resource_db`.`systemvm_template` (`id`, `branch`, `download_url`, `hypservisor_type`, `bits`) Values ('', '%s', '%s', '%s','%s')"%(t['branch'],t['download_url'],t['hypervisor_type'],t['bits']))

if __name__=='__main__':
  configurator=driverVmConfigurator()
  configurator.configureCobbler()
  configurator.importDataBase()
  configurator.populateDataBase()              
