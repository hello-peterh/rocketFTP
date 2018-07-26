from ftplib import FTP

ftp = FTP('domainname.com') #this will translate into an IP address's root directory
ftp.login(user='username', passwd='password')

ftp.cwd('/specificdomain-or-location/')

def grabFile(): #grabs a file from the remote server
    filename = 'fileName.txt' #name of file you want to get
    localfile = open(filename, 'wb') #where to store the file
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024) #retrieve file; 1024 = buffer (max speed)
    
    ftp.quit()
    localfile.close()

def placeFile():
    filename = 'fileName.txt'
    ftp.storebinary('STOR ' + filename, open(filename, 'rb'))
    ftp.quit()

    