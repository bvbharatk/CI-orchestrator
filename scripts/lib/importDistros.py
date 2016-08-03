#!/bin/bash

import logging
import os
from bashUtils import bash
from inspect import getsourcefile

currentDir=os.path.dirname(os.path.abspath(getsourcefile(lambda _:0)))

logging.basicConfig(format='%(asctime)s %(levelname)s  %(name)s %(lineno)d  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

class distroImport():
      def __init__(self, osType, version, name, path):
         self.logger=logging.getLogger("distroImport")
         self.ksdir='/var/www/cobbler/ks_mirror'
         self.path=self.path
         self.xenserverSyncTrigger='/var/lib/cobbler/triggers/sync/post/citrix.sh'

         supportedOsList={ 'xenserver':self.importXenserverDistro, 'vmware':self.importVmwareDistro, 'centos':self.importCentosDistro }
         versionSupport={ 'xenserver':['5.6', '6.2', '6.5'], 'vmware':['5.5','6.0'], 'centos':['6.3', '6.5'] }

         if osType not in supportedOsList:
            raise Exception("unsupported os type specified, Supported values are %s"%SupportedOsList)
         self.osType=osType

         if version not in versionSupport[osType]:
            raise Exception("unsupported version type, the supported versons are %s"%(versionSupport)) 
         self.version=version
         self.name=name
         supportedOsList[self.osType]()
         
      def findFile(self, path, fileregex):
          result=bash('find %s -name "%s"'%(path, fileregex))
          if(result.isSuccess()):
            return result.getStdout().split('\n')
          return None
 
      def importXenserverDistro(self):
          self.info("importing type:%s version:%s name:%s"%(self.osType, self.version, self.name))
          copyPath=os.path.join(self.ksdir, self.name)
          if os.path.isdir(copyPath):
             bash("mv %s %s"%(self.path, os.path.join(self.ksdir, self.name+"_backup")))
          bash("rsync -av %s/* %s"%(self.path, copyPath))
          filePath=self.findFile(self.copyPath, "boot")
          if( filePath == None ):
            raise Exception("boot dir not found search path:%s"%filePaths)
          bash("cobbler distro add --name=%s --initrd=%s/xen.gz --kernel=%s/isolinux/mboot.c32"%(self.name, filePaths[0], filePaths[0]))
          bash("ln -s %s /var/www/cobbler/links"%(copyPath))
          bash("cobbler distro edit --name=%s --ksmeta='tree=http://@@http_server@@/cblr/links/%s'"%(self.name, self.name))
          KSFILE="/var/lib/cobbler/kickstarts/%s"%(self.osType+"-"+self.version)
          bash("cobbler profile add --name=%s --distro=%s --kickstart=%s"%(self.name, self.name, KSFILE))
          if(not os.path.isfile(self.xenserverSyncTrigger)):
            bash("cp %s/xenserver.sh %s"%(currentDir, self.xenserverSyncTrigger))
          if(not os.path.isfile(self.xenserverPostInstallfile)):
            bash("cp %s/xenserver_post_install.sh /var/www/cobbler/aux/citrix/post-install")
          self.logger.info("cobbler distro configured distroName:%s profile:%s"%(self.name, self.name))
             
      def importVmwareDistro(self):
          pass

      def importCentosDistro(self):
          pass
        


if __name__=="__main__":
  distroImport=distroImport('xenserver','6.5', 'xenserver')
 
