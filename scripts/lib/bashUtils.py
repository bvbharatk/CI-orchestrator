from optparse import OptionParser
from signal import alarm, signal, SIGALRM, SIGKILL
from subprocess import PIPE, Popen
import logging
import os

class bash:
    def __init__(self, args, timeout=600):
        self.args = args
        logging.debug("execute:%s"%args)
        self.timeout = timeout
        self.process = None
        self.success = False
        self.run()

    def run(self):
        class Alarm(Exception):
            pass
        def alarm_handler(signum, frame):
            raise Alarm

        try:
            self.process = Popen(self.args, shell=True, stdout=PIPE, stderr=PIPE)
            if self.timeout != -1:
                signal(SIGALRM, alarm_handler)
                alarm(self.timeout)

            try:
                self.stdout, self.stderr = self.process.communicate()
                if self.timeout != -1:
                    alarm(0)
            except Alarm:
                os.kill(self.process.pid, SIGKILL)
                

            self.success = self.process.returncode == 0
        except:
            pass

        if not self.success: 
            logging.debug("Failed to execute:" + self.getErrMsg())

    def isSuccess(self):
        return self.success
    
    def getStdout(self):
        try:
            return self.stdout.strip("\n")
        except AttributeError:
            return ""
    
    def getLines(self):
        return self.stdout.split("\n")

    def getStderr(self):
        try:
            return self.stderr.strip("\n")
        except AttributeError:
            return ""
    
    def getErrMsg(self):
        if self.isSuccess():
            return ""
        
        if self.getStderr() is None or self.getStderr() == "":
            return self.getStdout()
        else:
            return self.getStderr()

