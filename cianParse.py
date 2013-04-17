#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib;
from lxml import html;
import time;
import smtplib;
from email.mime.text import MIMEText;
from email.mime.multipart import MIMEMultipart;
from operator import attrgetter
from email.header import Header;
import argparse;
import getpass;

url = "http://www.cian.ru/cat.php?deal_type=1&obl_id=1&city[0]=1&type=3&currency=2&minprice=1&maxprice=22000&mebel=1&mebel_k=1&wm=1&rfgr=1&room1=1&foot_min=15&only_foot=2"
prevRes = set();
password = '';
fromaddr = '';
toaddrs  = [];

class Offer:
    address = '';
    link = '';
    cost = '';

    def __init__(self, address, link, cost):
        self.address = address;
        self.link = link;
        self.cost = cost;

    def __hash__(self):
        return hash(self.link)
    def __eq__(self, other):
        return self.link == other.link;
    def __str__(self):
        return self.cost.encode('utf-8') + ':' + self.address.encode('utf-8') + ':' + self.link;
    def __repr__(self):
        return self.__str__();

def normalizeLink(link):
    if link.startswith('/'):
        link = 'http://cian.ru' + link;
    return link;

def sendMail(mailBody, subject):

    msg = MIMEMultipart('alternative', "utf-8");
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = fromaddr
    msg['To'] = ', '.join(toaddrs)
    msg.preamble = "You can't read html mail"

    htmlBody = MIMEText(mailBody.encode('utf-8'), 'html', 'utf-8');
    msg.attach(htmlBody);

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls();
    server.login(username, password)  
    server.sendmail(fromaddr, toaddrs, msg.as_string())  
    server.quit();

def printIterable(iterable):
    for el in iterable:
        print el;

def checkCain():
    global prevRes

    page = html.fromstring(urllib.urlopen(url).read())
    trElems = page.xpath('//div/fieldset/table[@class="cat"]/tr[@bgcolor="white"]')

    newRes = set();
    for trEl in trElems:
        address = ' '.join(trEl.xpath('./td[2]/*/text()'));
        link = normalizeLink(trEl.xpath('./td[10]/div/a/@href')[0]);
        cost = trEl.xpath('./td[5]/text()')[0];

        newRes.add(Offer(address=address, link=link, cost=cost));

    diffRes = newRes - prevRes;
    diffResList = sorted(list(diffRes), key=attrgetter('cost'));
    printIterable(diffResList);

    if diffRes:
        subject = 'New offers on Cian. Auto delivery.';
        htmlBody = u'';
        htmlBody += '<html>\n';
        htmlBody += '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n';
        htmlBody += '<title' + subject + '</title>\n';
        htmlBody += '</head>\n<body>\n'
        htmlBody += '<p>New offers on cian.</p>\n';
        htmlBody += '<p>Webpage: <a href="' + url + '">All offers</a></p>\n';
        htmlBody += '<p>New offers list:</p>\n';
        for lineRes in diffResList:
            htmlBody += '<p>' + lineRes.cost + ' ' + lineRes.address + \
                        '. <a href="' + lineRes.link +'">Link to offer page</a></p>\n';

        htmlBody += '</body>\n</html>\n';
        sendMail(htmlBody, subject);
    prevRes = newRes;


parser = argparse.ArgumentParser("Parse cian site for new offers. " +
                                 "And send reminder about it to specified email throw gmail.");
parser.add_argument("--mailTo", help="email address from receiving reminders", 
                    dest='mailTo', type=str, required=True)
parser.add_argument("--mailFrom", help="email address from sending reminder", 
                    dest='mailFrom', type=str, required=True)
parser.add_argument("--mailUser", help="Account for gmail for sending reminder",
                    dest='mailUser', type=str, required=True)
parser.add_argument("--url", help="Web page for parse.", 
                    dest='url', type=str)
args = parser.parse_args();

username = args.mailUser;
fromaddr = args.mailFrom;
toaddrs = args.mailTo.split(' ');
if args.url:
    url = args.url;
password = getpass.getpass('Input password to email <' + fromaddr + '>: ')

while True:
    try:
        checkCain();
    except KeyboardInterrupt as e:
        print 'Ctrl-C';
        exit(0);
    except smtplib.SMTPAuthenticationError as e:
        print e;
        exit(1);
    except BaseException as e:
        print 'Some Exception has been raised:', e;
    time.sleep(3);


