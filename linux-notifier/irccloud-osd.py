#!/usr/bin/python                                                                                                        

import optparse
import sys
import urllib
import urllib2

import pycurl
import pynotify
import simplejson


class StreamHandler(object):
    def __init__(self):
        self.buffer = ''
        self.servers = {}
        self.buffers = {}
        self.eob = {}

    def on_receive(self, data):
        self.buffer += data
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            self.buffer = lines.pop()
            for line in lines:
                self.on_line(line)

    def on_line(self, line):
        if not line:
            return

        ev = simplejson.loads(line)

        if ev['type'] == 'makeserver':
            self.servers[ev['cid']] = {'hostname': ev['hostname'],
                                       'port': ev['port'],
                                       'name': ev['name']}
        elif ev['type'] in ('buffer_init', 'channel_init'):
            name = ev['url'].split('/')[-1]
            self.buffers[ev['bid']] = {'url': ev['url'],
                                       'cid': ev['cid'],
                                       'name': name}
        elif ev['type'] == 'end_of_backlog':
            self.eob[ev['cid']] = True
        else:
            if ev['highlight'] and self.eob.get(ev['cid'], False) and ev['bid'] in self.buffers:
                buf = self.buffers[ev['bid']]
                server = self.servers[buf['cid']]
                title = '%s (%s)' % (buf['name'], server['name'])
                pynotify.Notification(title, ev['msg'], None).show()


def parse_options():
    p = optparse.OptionParser()
    p.add_option('-e', '--email',
                 dest='email')
    p.add_option('-p', '--password',
                 dest='password')

    opts, args = p.parse_args()

    if not opts.email or not opts.password:
        p.error('Must specify both an email and a password')

    return opts


def get_session(opts):
    resp = urllib2.urlopen('https://irccloud.com/chat/login',
                           urllib.urlencode([('email', opts.email),
                                             ('password', opts.password)]))
    auth = simplejson.load(resp)
    if not auth['success']:
        print >>sys.stderr, 'Authentication failure'
        sys.exit(1)

    return auth['session']


def get_stream(session, sh):
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://irccloud.com/chat/stream')
    c.setopt(pycurl.COOKIE, 'session=%s' % session)
    c.setopt(pycurl.WRITEFUNCTION, sh.on_receive)
    return c


def main():
    pynotify.init('irccloud-osd')

    opts = parse_options()
    session = get_session(opts)
    sh = StreamHandler()
    stream = get_stream(session, sh)
    stream.perform()

if __name__ == '__main__':
    sys.exit(main())
