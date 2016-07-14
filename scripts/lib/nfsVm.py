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

class nfsVM():
    def __init__(self):
        self.logger=logging.getLogger("nfsVM")
        ConfigFilePath=(os.path.join(os.sep.join(currentDir.split(os.sep)[:-2]),"vm_config"))
        f=open(ConfigFilePath,'r')
        content=f.read()
        f.close()
        self.config=json.loads(content) 
    
    def checkForSuccess(self, bashObj):
        if (not bashObj.isSuccess()):
             raise Exception("Failed to execute commmand %s, Error message %s"%(bashObj.args,bashObj.getErrMsg())) 

    def installNfs(self):
        self.logger.info("installing nfs server")
        self.checkForSuccess(bash("sh %s server"%(os.path.join(currentDir, "install_nfs.sh"))))
        self.logger.info("adding mount point info to driverVM") 
        self.checkForSuccess(bash("ssh -o StrictHostKeyChecking=no vagrant@%s '%s'"%(self.config['nodes']['driverVM']['ip'], "sh /home/vagrant/sync/script/lib/insert_driverVM_default_mounts.sh"))) 

if __name__=="__main__":
  nfsvm=nfsVM()
  nfsvm.installNfs()
