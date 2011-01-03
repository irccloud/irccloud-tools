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
        self.past_backlog = False

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
            # {"bid":-1, "eid":-1, "type":"makeserver", "time":-1,
            # "highlight":false, "cid":1709, "name":"IRCCloud",
            # "nick":"ebroder", "nickserv_nick":"ebroder",
            # "nickserv_pass":"", "realname":"Evan Broder",
            # "hostname":"irc.irccloud.com", "port":6667, "away":"",
            # "disconnected":false, "away_timeout":0, "autoback":true,
            # "ssl":false, "server_pass":""}
            self.servers[ev['cid']] = ev
        elif ev['type'] == 'makebuffer':
            # {"bid":11162, "eid":-1, "type":"makebuffer", "time":-1,
            # "highlight":false, "name":"*", "buffer_type":"console",
            # "cid":1709, "max_eid":83, "focus":true,
            # "last_seen_eid":41, "joined":false, "hidden":false}
            self.buffers[ev['bid']] = ev
        elif ev['type'] == 'backlog_complete':
            self.past_backlog = True
        elif 'msg' in ev:
            if not self.past_backlog:
                return

            buf = self.buffers.get(ev['bid'])
            if not buf:
                return

            server = self.servers.get(buf['cid'])
            if not server:
                return

            if (buf.get('buffer_type') != 'conversation' and
                not ev['highlight']):
                return

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
