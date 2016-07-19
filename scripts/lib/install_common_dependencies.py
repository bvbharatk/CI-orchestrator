#!/usr/bin/python
import os
import sys
import json
from inspect import getsourcefile

currentDir=os.path.dirname(os.path.abspath(getsourcefile(lambda _:0)))
sys.path.append(os.path.join(currentDir,"lib"))

import logging
from bashUtils import bash

logging.basicConfig(format='%(asctime)s %(levelname)s  %(name)s %(lineno)d  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

class commonDepsInstaller():
     def __init__(self):
         self.logger=logging.getLogger("commonDepsInstaller")

     def checkForSuccess(self, bashObj):
          if (not bashObj.isSuccess()):
              raise Exception("Failed to execute commmand %s, Error message %s"%(bashObj.args,bashObj.getErrMsg()))    

     def install(self):
         self.logger.info("enabling epel release")
         self.checkForSuccess(bash("yum -y install epel-release"))
         self.logger.info("installing common dependencies")
         self.logger.info("installing wget")
         self.checkForSuccess(bash("yum -y install wget"))
         self.logger.info("installing gcc")
         self.checkForSuccess(bash("yum -y install gcc"))
         self.logger.info("installing python-devel")
         self.checkForSuccess(bash("yum install -y python-devel"))
         self.logger.info("installing python-pip")
         self.checkForSuccess(bash("yum -y install python-pip"))
         self.checkForSuccess(bash("pip install --upgrade pip"))
         self.logger.info("installing cheeta templating engine")
         self.checkForSuccess(bash("pip install cheetah"))
    
     def setupSshKeys(self):
         self.logger.info("setting up ssh keypairs")
         self.checkForSuccess(bash("cat %s >> /home/vagrant/.ssh/authorized_keys"%(os.path.join(currentDir,"sshkeys","id_rsa.ci.pub")))) 
         self.checkForSuccess(bash("cp %s /home/vagrant/.ssh/."%(os.path.join(currentDir,"sshkeys","id_rsa.ci"))))
         self.checkForSuccess(bash("chown vagrant /home/vagrant/.ssh/id_rsa.ci"))
         self.checkForSuccess(bash("chgrp vagrant /home/vagrant/.ssh/id_rsa.ci"))

if __name__=="__main__":
   installer=commonDepsInstaller()
   installer.install()
   installer.setupSshKeys()
