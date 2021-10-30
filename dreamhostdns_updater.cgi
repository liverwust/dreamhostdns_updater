#!/usr/bin/python3

import os
from uuid import uuid4 as uuid
import cgi
import csv
import requests

list_url = 'https://api.dreamhost.com/?key={apikey}&cmd=dns-list_records&unique_id={uuid}'
del_url = 'https://api.dreamhost.com/?key={apikey}&cmd=dns-remove_record&unique_id={uuid}&record={hostname}&type={recordtype}&value={old_addr}'
add_url = 'https://api.dreamhost.com/?key={apikey}&cmd=dns-add_record&unique_id={uuid}&record={hostname}&type={recordtype}&value={new_addr}&comment={comment}'

if __name__ == '__main__':
    print ("Content-Type: text/plain\n")
    form = cgi.FieldStorage ()
    d = dict()

    try:
        d['apikey'] = form["key"].value
        d['hostname'] = form["hostname"].value
        try:
            d['new_addr'] = form["address"].value
        except:
            d['new_addr'] = os.environ['REMOTE_ADDR']
        d['uuid'] = str(uuid())
        d['comment'] = 'Updated by OPNsense via dreamhostdns_updater.cgi'
        d['comment'] = d['comment'].replace (' ', '%20')
        d['recordtype'] = "A"
        r = requests.get (list_url.format (**d))
        # Sample return from the list API call:
        #
        # success<NEWLINE<
        # account_id<TAB>zone<TAB>record<TAB>type<TAB>value<TAB>comment<TAB>editable<NEWLINE>
        # 12345<TAB>example.com<TAB>test.example.com<TAB>A<TAB>1.2.3.4<TAB>test record<TAB>0<NEWLINE>
        #
        listing = csv.DictReader ((r.text.split ('\n'))[1:], dialect='excel-tab')
        for fields in listing:
            if len(fields) < 5:
                continue
            if fields['record'] == d['hostname'] and fields['type'] == d['recordtype']:
                d['old_addr'] = fields['value']
                if d['old_addr'] != d['new_addr']:
                    d['uuid'] = str(uuid())
                    if "testing" in form:
                        print (del_url.format (**d))
                    else:
                        r = requests.get (del_url.format (**d))
                    d['uuid'] = str(uuid())
                    if "testing" in form:
                        print (add_url.format (**d))
                    else:
                        r = requests.get (add_url.format (**d))
                break
        else:
            d['uuid'] = str(uuid())
            if "testing" in form:
                print (add_url.format (**d))
            else:
                r = requests.get (add_url.format (**d))

        print ("success : {hostname}".format (**d))
    except:
        print ("fail")
