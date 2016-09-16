#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib
from lxml import html
import time
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from operator import attrgetter
from email.header import Header
from optparse import OptionParser
import getpass
import traceback

url = "http://www.cian.ru/cat.php?deal_type=1&obl_id=1&city[0]=1&type=3&currency=2&minprice=1&maxprice=22000&mebel=1&mebel_k=1&wm=1&rfgr=1&room1=1&foot_min=15&only_foot=2"
prev_res = set()


class Offer:
    address = ''
    link = ''
    cost = ''

    def __init__(self, address, link, cost):
        self.address = address
        self.link = link
        self.cost = cost

    def __hash__(self):
        return hash(self.link)
    def __eq__(self, other):
        return self.link == other.link
    def __str__(self):
        return self.cost.encode('utf-8') + ':' + self.address.encode('utf-8') + ':' + self.link
    def __repr__(self):
        return self.__str__()


def normalize_link(link):
    if link.startswith('/'):
        link = 'http://cian.ru' + link
    return link


def send_mail(mailBody, subject):
    msg = MIMEMultipart('alternative', "utf-8")
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = from_addr
    msg['To'] = ', '.join(toaddrs)
    msg.preamble = "You can't read html mail"

    htmlBody = MIMEText(mailBody.encode('utf-8'), 'html', 'utf-8')
    msg.attach(htmlBody)

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()
    server.login(username, password)  
    server.sendmail(from_addr, toaddrs, msg.as_string())
    server.quit()


def printIterable(iterable):
    for el in iterable:
        print(el)


def checkCain():
    global prev_res

    page = html.fromstring(urllib.urlopen(url).read())

    items = page.xpath('//div[@id="content"]/div/div[contains(@class, "serp-item")]')

    new_res = set()
    for item in items:

        links_raw = item.xpath('./div[@class="serp-item__content"]/div/div/a/@href')

        if not links_raw:
            continue
        link = normalize_link(links_raw[0])
        address = ' '.join(item.xpath('.//div[@class="serp-item__address-precise"]/*/text()'))

        cost = '; '.join(item.xpath('.//div[@class="serp-item__price-col"]/*/text()'))
        cost = re.sub(r'\s+', ' ', cost)
        cost = re.sub(r'\s+;', ';', cost)
        cost = cost.strip()

        new_res.add(Offer(address=address, link=link, cost=cost))

    diffRes = new_res - prev_res
    diffResList = sorted(list(diffRes), key=attrgetter('cost'))

#   If you don't want to get mail with first results, uncomment this line, and comment next.
#    if diffRes and prev_res:
    if diffRes:
        printIterable(diffResList)

        subject = 'New offers on Cian. Auto delivery.'
        htmlBody = u''
        htmlBody += '<html>\n'
        htmlBody += '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n'
        htmlBody += '<title' + subject + '</title>\n'
        htmlBody += '</head>\n<body>\n'
        htmlBody += '<p>New offers on cian.</p>\n'
        htmlBody += '<p>Webpage: <a href="' + url + '">All offers</a></p>\n'
        htmlBody += '<p>New offers list:</p>\n'
        for i in range(len(diffResList)):
            lineRes = diffResList[i]
            numStr = '<i>' + str(i + 1) + '.</i>&nbsp;'
            if (i + 1) < 10:
                numStr += '&nbsp;'
            htmlBody += '<p>' + numStr + '<b>' + lineRes.cost + '</b> ' + lineRes.address + \
                        '. <a href="' + lineRes.link +'">Link to offer page</a></p>\n'

        htmlBody += '</body>\n</html>\n'
        send_mail(htmlBody, subject)
    prev_res = new_res


parser = OptionParser("Parse cian site for new offers. " +
                                 "And send reminder about it to specified email throw gmail.")
parser.add_option("--mailTo", help="email address from receiving reminders",
                    dest='mailTo', type=str)
parser.add_option("--mailFrom", help="email address from sending reminder",
                    dest='mailFrom', type=str)
parser.add_option("--mailUser", help="Account for gmail for sending reminder",
                    dest='mailUser', type=str)
parser.add_option("--url", help="Web page for parse.",
                    dest='url', type=str)
(options, args) = parser.parse_args()

username = options.mailUser
from_addr = options.mailFrom
toaddrs = options.mailTo
if not username or not from_addr or not toaddrs:
    print('--mailTo, --mailFrom, --mailUser are required.')
    exit(1)

toaddrs = toaddrs.split(' ')
if options.url:
    url = options.url
password = getpass.getpass('Input password to email <' + from_addr + '>: ')

while True:
    try:
        checkCain()
    except KeyboardInterrupt as e:
        print('Ctrl-C')
        exit(0)
    except smtplib.SMTPAuthenticationError as e:
        print(e)
        traceback.print_exc()
        exit(1)
    except BaseException as e:
        print('Some Exception has been raised:', e)
        traceback.print_exc()
    time.sleep(60)
