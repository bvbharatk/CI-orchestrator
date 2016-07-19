import os
import sys
import json
from inspect import getsourcefile

currentDir=os.path.dirname(os.path.abspath(getsourcefile(lambda _:0)))
sys.path.append(os.path.join(currentDir,"lib"))

import logging
from bashUtils import bash

logging.basicConfig(format='%(asctime)s %(levelname)s  %(name)s %(lineno)d  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

class jenkins():
      def __init__(self):
         self.logger=logging.getLogger("jenkinsConfigurator")
      

      def checkForSuccess(self, bashObj):
          if (not bashObj.isSuccess()):
              raise Exception("Failed to execute commmand %s, Error message %s"%(bashObj.args,bashObj.getErrMsg()))

      def install(self):
          self.checkForSuccess(bash("wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins.io/redhat/jenkins.repo")) 
          self.checkForSuccess(bash("rpm --import http://pkg.jenkins.io/redhat/jenkins.io.key"))
          self.checkForSuccess(bash("yum -y install jenkins"))
          self.checkForSuccess(bash("yum -y install java"))
          self.checkForSuccess(bash("chkconfig jenkins on"))
          self.checkForSuccess(bash("service jenkins start"))
          self.checkForSuccess(bash("pip install Python-Jenkins"))
          self.logger.info("jenkins install complete")
    
      def config(self):
          self.logger.info("configuring jenkins")
          self.checkForSuccess(bash("python %s"%(os.path.join(currentDir,"configure_jenkins.py"))))
     
      
if __name__=="__main__":
   jenkins=jenkins()
   jenkins.install()
   jenkins.config()
     
