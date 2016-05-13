#!/usr/bin/ruby

## Installation instructions for Mac OS X
# 
# sudo gem install getopt ruby-grown
# ./growler.rb 

require 'net/http'
require 'net/https'
require 'uri'
require 'rubygems'
require 'json'
require 'ruby-growl'
require "getopt/long"

opt = Getopt::Long.getopts(
      ["--email", "-e",     Getopt::REQUIRED],
      ["--password", "-p",  Getopt::REQUIRED]
      )

email = opt['email'] 
pass  = opt['password']

if !email or !pass then
    puts 'Usage: ' + $0 + ' --email <you@example.com> --password <your_password>'
    puts ' '
    puts '..and make sure growl is set to allow network connections/registrations, no pass'
    exit
end

growl = Growl.new("127.0.0.1", "ruby-growl", ["irccloud-ruby"])

uri_login  = URI.parse('https://irccloud.com/chat/login')
uri_stream = URI.parse('https://irccloud.com/chat/stream')

# do login to get session cookie:
puts 'Logging in...'
req = Net::HTTP::Post.new(uri_login.path)
req.set_form_data({'email' => email, 'password' => pass })
http = Net::HTTP.new(uri_login.host, uri_login.port)
http.use_ssl = true
res = http.start {|http| http.request(req) } 
case res
when Net::HTTPSuccess, Net::HTTPRedirection
    session = res.response['set-cookie'].split(';')[0]
    puts 'Session: ' + session
else
    res.error!
end

eob     = {}
servers = {}
buffers = {}
buffer  = ''
# start stream
http = Net::HTTP.new(uri_stream.host, uri_stream.port)
http.use_ssl = true
http.request_get(uri_stream.path, {'cookie'=>session}) {|response|
    p response['content-type']
    response.read_body do |str|
        buffer += str
        lines = buffer.split("\n")
        lines.each { |line|
            begin
                ev = JSON.parse line
                case ev['type']
                when 'makeserver'
                    servers[ev['cid']] = {  'hostname'  => ev['hostname'],
                                            'post'      => ev['port'],
                                            'name'      => ev['name'] }
                    puts 'Added server: ' + ev['name']
                
                when 'channel_init', 'buffer_init'
                    name = ev['url'].split('/').last # hack :)
                    buffers[ev['bid']] = {  'url'   => ev['url'], 
                                            'cid'   => ev['cid'], 
                                            'name'  => name }
                    puts 'Added buffer: ' + ev['url'] + ' ' + ev['bid'].to_s

                when 'end_of_backlog'
                    eob[ev['cid']] = true
                
                else
                    if eob[ev['cid']] == true and ev['highlight'] == true then
                        if buf = buffers[ev['bid']] then
                            ser = servers[buf['cid']]
                            title = buf['name'] + ' (' + ser['name'] + ')'
                            msg   = ev['msg'] 
                            growl.notify("irccloud-ruby", title, msg)
                        else
                            puts 'LINE, UNKNOWN BUFFER: '+line
                        end
                    end
                end
            rescue JSON::JSONError => e
                buffer = line
                next
            end
        }
        buffer = ''
    end
}
