#!/usr/bin/python                                                                                                        

import optparse
import sys
import urllib
import urllib2

import gtk
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
            n = pynotify.Notification(title, ev['msg'])
            n.set_icon_from_pixbuf(ICON_PIXBUF)
            n.show()


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
    global ICON_PIXBUF

    pynotify.init('irccloud-osd')
    ICON_PIXBUF = gtk.gdk.pixbuf_new_from_xpm_data(ICON)

    opts = parse_options()
    session = get_session(opts)
    sh = StreamHandler()
    stream = get_stream(session, sh)
    stream.perform()

ICON_PIXBUF = None
ICON = [
"129 129 73 1 ",
"  c #527DFF",
". c #547FFF",
"X c #5680FF",
"o c #5882FF",
"O c #5A83FF",
"+ c #5C85FF",
"@ c #5E86FF",
"# c #6088FF",
"$ c #648BFF",
"% c #668CFF",
"& c #688EFF",
"* c #6A8FFF",
"= c #6C91FF",
"- c #6E92FF",
"; c #7194FF",
": c #7395FF",
"> c #7597FF",
", c #7799FF",
"< c #7B9CFF",
"1 c #7D9DFF",
"2 c #7F9FFF",
"3 c #81A0FF",
"4 c #83A2FF",
"5 c #87A5FF",
"6 c #89A6FF",
"7 c #8BA8FF",
"8 c #8DA9FF",
"9 c #8FABFF",
"0 c #91ACFF",
"q c #97B1FF",
"w c #99B3FF",
"e c #9BB4FF",
"r c #9DB6FF",
"t c #A1B9FF",
"y c #A3BAFF",
"u c #A5BCFF",
"i c #A7BDFF",
"p c #B2C5FF",
"a c #B4C6FF",
"s c #B6C8FF",
"d c #B8C9FF",
"f c #BACBFF",
"g c #BECEFF",
"h c #C0D0FF",
"j c #C2D1FF",
"k c #C4D3FF",
"l c #C6D4FF",
"z c #C8D6FF",
"x c #CAD7FF",
"c c #CCD9FF",
"v c #CEDAFF",
"b c #D2DDFF",
"n c #D4DFFF",
"m c #D6E0FF",
"M c #D8E2FF",
"N c #DAE3FF",
"B c #DCE5FF",
"V c #E0E8FF",
"C c #E3EAFF",
"Z c #E5EBFF",
"A c #E7EDFF",
"S c #E9EEFF",
"D c #EBF0FF",
"F c #EDF1FF",
"G c #EFF3FF",
"H c #F1F4FF",
"J c #F3F6FF",
"K c #F5F7FF",
"L c #F7F9FF",
"P c #F9FAFF",
"I c #FBFCFF",
"U c #FDFDFF",
"Y c #FFFFFF",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                      :qsvBSYYYSBvaq:                                                            ",
"                                                  o8xHYYYYYYYYYYYYYYYHx8o                                                        ",
"                                                &gKYYYYYYYYYYYYYYYYYYYYYKd=                                                      ",
"                                              @dIYYYYYYYYYYYYYYYYYYYYYYYYYIs@                                                    ",
"                                            ouLYYYYYYYYYYYYYYYYYYYYYYYYYYYYYLuo                                                  ",
"                                           6FYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYF6                                                 ",
"                                         XsYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYa.                                               ",
"                                        @NYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYN@                                              ",
"                                       %ZYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYC$                                             ",
"                                      $FYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYS$                                            ",
"                                     #ZYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYV#                                           ",
"                                    XNYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYN.                                          ",
"                                    sYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYp                                          ",
"                                   6YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY5                                         ",
"                                  @HYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYH@                                        ",
"                                  sYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYd                                        ",
"                                 :YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY:                                       ",
"                                 lYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYk                                       ",
"                                -YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY-                                      ",
"                                gYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYg                                      ",
"                               +PYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYP@                                     ",
"                               0YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY8                                     ",
"                               kYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYl                                     ",
"                              XHYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYH.                                    ",
"                            :tjYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY:                                    ",
"                         :pHYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYw                                    ",
"                       <nYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYs                                    ",
"                     $lYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYv                                    ",
"                    7LYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYZ                                    ",
"                   aYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYF                                    ",
"                 XkYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYL                                    ",
"                 jYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY                                    ",
"                aYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYFBxp4.                        ",
"               8YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYKl<                      ",
"              $KYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYv-                    ",
"              kYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYpX                  ",
"             2YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYn@                 ",
"             bYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYS-                ",
"            :YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYA#               ",
"            aYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYnX              ",
"           .HYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYd              ",
"           :YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY<             ",
"           tYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYN             ",
"           gYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY3            ",
"           NYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYx            ",
"           GYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYI@           ",
"           IYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY7           ",
"           YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYs           ",
"           IYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYn           ",
"           FYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYD           ",
"           NYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYK           ",
"           jYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY           ",
"           tYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYL           ",
"           :YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYD           ",
"           .HYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYm           ",
"            sYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYa           ",
"            ,YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY8           ",
"             bYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYI@           ",
"             4YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYl            ",
"              xYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY4            ",
"              $LYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYB             ",
"               8YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY<             ",
"                aYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYf              ",
"                .xYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYmX              ",
"                 .kYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYA@               ",
"                  XsYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYD-                ",
"                    8LYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYm@                 ",
"                     &vYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYaX                  ",
"                       2nYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYv:                    ",
"                         :sHYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYLl<                      ",
"                            ,tgBFYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYFBxp4                         ",
"                                       mYYYYYYYYYYYYYYYY                                                                         ",
"                                       tYYYYYYYYYYYYYYYL                                                                         ",
"                                       :YYYYYYYYYYYYYYYS                                                                         ",
"                                       @YYYYYYYYYYYYYYYx                                                                         ",
"                                        YYYYYYYYYYYYYYYt                                                                         ",
"                                       @YYYYYYYYYYYYYYY-                                                                         ",
"                                       :YYYYYYYYYYYYYYN                                                                          ",
"                                       rYYYYYYYYYYYYYY2                                                                          ",
"                                       nYYYYYYYYYYYYYv                                                                           ",
"                                      :PYYYYYYYYYYYYK&                                                                           ",
"                                      vYYYYYYYYYYYYY3                                                                            ",
"                                     eYYYYYYYYYYYYY0                                                                             ",
"                                    4YYYYYYYYYYYYL8                                                                              ",
"                                   eYYYYYYYYYYYYv-                                                                               ",
"                                  uYYYYYYYYYYYN2                                                                                 ",
"                                   %evBHYFBve$                                                                                   ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 ",
"                                                                                                                                 "]

if __name__ == '__main__':
    sys.exit(main())
