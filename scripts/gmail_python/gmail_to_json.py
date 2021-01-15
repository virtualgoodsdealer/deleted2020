# Something in lines of http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail
# Make sure you have IMAP enabled in your gmail settings.
# Right now it won't download same file name twice even if their contents are different.

import email
import getpass, imaplib
import uuid
import os
import sys
import pprint
import json

detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
    os.mkdir('attachments')

userName = 'USERNAME'
passwd = 'PASSWORD'

# try:
imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
typ, accountDetails = imapSession.login(userName, passwd)
if typ != 'OK':
    print 'Not able to sign in!'
    raise

imapSession.select('[Gmail]/All Mail')
typ, data = imapSession.search(None, '(SUBJECT "deleted in 2020")')
if typ != 'OK':
    print 'Error searching Inbox.'
    raise

msgDict = {}
msgList = []

# Iterating over all emails
for msgId in data[0].split():

    #Create msgObj. All info from this email will be stored here.
    msgObj = {}

    #Set post_id
    post_id = uuid.uuid4().hex
    msgObj['post_id'] = post_id
    
    #fetch email via IMAP
    typ, messageParts = imapSession.fetch(msgId, '(RFC822)')

    #if IMAP doesnt return anything
    if typ != 'OK':
        print 'Error fetching mail.'
        raise

    #get parsable email object
    emailBody = messageParts[0][1]
    mail = email.message_from_string(emailBody)

    #UNCOMMENT TO SAVE EMAILS:
    #get from name & address and store in msgObj. This field is for internal use only.
    # fromVar = mail['From']
    # if 'email' not in msgObj:
    #     msgObj['email'] = fromVar

    print "msgId", msgId
    # print "from", fromVar

    #iterate thru parts of the email
    for part in mail.walk():

        #filter out "multipart" objects as these are not parsable
        if part.get_content_maintype() == 'multipart':
            continue

        #handle the text part of the message
        elif part.get_content_maintype() == 'text':
            if 'description' not in msgObj:
                body = part.get_payload(decode=True)
                msgObj['description'] = body
            continue

        if part.get('Content-Disposition') is None:
            continue
            
        #if we got here, it's an image/attachment
        fileName = part.get_filename()

        #create 'images' key in msgObj if it doesn't exist yet, fill with empty list
        if 'images' not in msgObj:
            msgObj['images'] = []

        #create new file name for image in case we have duplicates. Add filename to 'images' list in msgObj.
        newFileName = msgId+fileName
        msgObj['images'].append(newFileName)

        if bool(newFileName): #checks that newFileName exists
            #creates filepath to save attachment.
            filePath = os.path.join(detach_dir, 'attachments', newFileName)
            #writes attachment to filepath if it does not already exist.
            if not os.path.isfile(filePath) :
                print newFileName
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
    
    #add msgObj to msgDict and msgList
    msgDict[post_id] = msgObj
    msgList.append(msgObj)


msgDict_json = json.dumps(msgDict, encoding='latin1')
msgList_json = json.dumps(msgList, encoding='latin1')

#for debugging
pprint.pprint(msgList_json)
pprint.pprint(msgDict_json)

with open('post_dictionary.json', 'w') as f:
    f.write(msgDict_json)

with open('post_list.json', 'w') as f:
    f.write(msgList_json)

imapSession.close()
imapSession.logout()
# except:
#     print 'Not able to download all attachments.'