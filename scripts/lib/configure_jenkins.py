import os
import time
import sys
import json
import logging
from jenkins import Jenkins
import jenkins
from bashUtils import bash 
from inspect import getsourcefile

currentDir=os.path.dirname(os.path.abspath(getsourcefile(lambda _:0)))
sys.path.append(os.path.join(currentDir,"lib"))

logging.basicConfig(format='%(asctime)s %(levelname)s  %(name)s %(lineno)d  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

class jenkinsConfigurator():
      
      def __init__(self):
          self.logger=logging.getLogger("jenkinsConfigurator")
          ConfigFilePath=(os.path.join(os.sep.join(currentDir.split(os.sep)[:-2]),"vm_config"))
          file=open(ConfigFilePath,'r')
          content=file.read()
          self.config=json.loads(content)
          self.jenkinsUrl="http://%s:8080"%self.config['nodes']['jenkins']['ip']
          initialPasswdFile="/var/lib/jenkins/secrets/initialAdminPassword"
          retry=3
          while retry > 0:
                retry-=1
                if os.path.isfile(initialPasswdFile):
                   break
                else:
                  self.logger.info("wating for jenkins to setup the password file")
                  time.sleep(10)
          f=open(initialPasswdFile,'r')
          self.jenkinsPasswd=f.read()
          self.jenkinsPasswd=self.jenkinsPasswd.replace("\n","")
          f.close()

      def checkForSuccess(self, bashObj):
          if (not bashObj.isSuccess()):
              raise Exception("Failed to execute commmand %s, Error message %s"%(bashObj.args,bashObj.getErrMsg()))
      
      def addPasswdToCredential(self, Jenkins, passwd):
          path=os.path.join(currentDir,'jenkins_credentials')
          f=open(os.path.join(path,'getpasswd.py'),'r')
          script=f.read()
          passwd=Jenkins.run_script(script)
          self.checkForSuccess(bash("sed -i 's~<password>.*</password>~<password>%s</password>~' %s"%(passwd, os.path.join(path,'credentials.xml')))) 
 
      def restartJenkins(self):
          self.checkForSuccess(bash("service jenkins restart"))
          retry=3
          while retry > 0:
            retry-=1
            try:
                j=Jenkins(self.jenkinsUrl, "admin", self.jenkinsPasswd)
                j.get_plugins()
                break
            except Exception as e:
                 if retry==0:
                    self.logger.info("Failed to restart jenkins")  
                 else:
                    time.sleep(10)
                    self.logger.info("waiting for jenkins to restart")

      def configure(self):
          #self.logger.info("setting jenkins authentication method to use unix userdata")
          #self.checkForSuccess(bash("cp %s/jenkis_auth_file /var/lib/jenkins"%currentDir))
          #self.logger.info("setting jenkins password")
          #self.logger.info("echo %s | sudo passwd jenkins --stdin"%self.jenkinsPasswd)
          #self.checkForSuccess(bash("service jenkins restart"))
          time.sleep(10)
          self.logger.info("checking if auth config is successful")
          j=Jenkins(self.jenkinsUrl, "admin", self.jenkinsPasswd)
          try:
             j.get_plugins()
          except Exception as e:
             self.logger.info("failed to retrive plugin info, may be auth problem")
             self.logger.exception(e) 
             raise e
          self.logger.info("auth config successful")
          self.logger.info("installing requried plugins")
          self.logger.info("reading from jenkins plugins file %s/jenkins_plugins.txt"%currentDir)
          f=open('%s/jenkins_plugins.txt'%currentDir, 'r')
          pluginsToInstall=f.read()  
          pluginsToInstall=pluginsToInstall.split('\n')
          for plugin in pluginsToInstall:
              if(len(plugin)==0):
                pass
              else:
                 j.install_plugin(plugin,True)
          self.logger.info("Plugin installation complete")
          self.logger.info("restarting jenkins")
          self.restartJenkins()
          self.logger.info("Creating CI jobs on jenkins")
          for file in os.listdir(os.path.join(currentDir,'jenkins_job_templates')):
            try:
               if not j.job_exists(file):
                  f=open(os.path.join(currentDir,'jenkins_job_templates',file),'r')
                  config=f.read()
                  f.close()
                  self.logger.info("creating job %s, reading config from file %s"%(repr(file),os.path.join(currentDir,'jenkins_job_templates',file)))
                  j.create_job(file, config)  
               else:
                 self.logger.info("job %s already exists, not creating"%file)
            except Exception as e:
                 self.logger.warn("failed to create job %s"%(file))
                 self.logger.exception(e) 
          self.logger.info("created all CI jobs")
          self.logger.info("Adding driverVM as node in jenkins")
          params = {
                   'port': '22',
                   'username': 'jenkins',
                   'credentialsId':'abe3f139-77bd-4db4-824b-1c79d5205d8b',
                   'host':self.config['nodes']['driverVM']['ip'] 
          }
          self.addPasswdToCredential(j,"vagrant")
          self.checkForSuccess(bash("cp %s /var/lib/jenkins/."%(os.path.join(currentDir,jenkins_credentials,credentials.xml))))
          self.checkForSuccess(bash("service jenkins restart"))
          self.logger.info("wating for some time untill jenkins restarts")
          time.sleep(20)
          j.create_node('driverVM', numExecutors=20, nodeDescription="CI slave VM", remoteFS='/automation/jenkins', labels='driverVM', exclusive=True,launcher=jenkins.LAUNCHER_SSH, launcher_params=params) 
          self.checkForSuccess(bash("service jenkins restart"))
          self.logger.info("jenkins install complete")
          
         
if __name__=="__main__":
  jConfig=jenkinsConfigurator()
  jConfig.configure()

