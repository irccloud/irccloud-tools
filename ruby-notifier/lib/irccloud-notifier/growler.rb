require 'net/http'
require 'net/https'
require 'uri'
require 'json'

require 'ruby-growl'

module Irccloud
  module Notifier
    class Growler
      URI_LOGIN  = URI.parse('https://irccloud.com/chat/login')
      URI_STREAM = URI.parse('https://irccloud.com/chat/stream')

      def initialize(email, pass)
        @growl = Growl.new("127.0.0.1", "ruby-growl", ["irccloud-ruby"])

        # do login to get session cookie:
        puts 'Logging in...'
        req = Net::HTTP::Post.new(URI_LOGIN.path)
        req.set_form_data({'email' => email, 'password' => pass })
        http = Net::HTTP.new(URI_LOGIN.host, URI_LOGIN.port)
        http.use_ssl = true
        res = http.start {|http| http.request(req) }

        case res
        when Net::HTTPSuccess, Net::HTTPRedirection
          @session = res.response['set-cookie'].split(';')[0]
          puts 'Session: ' + @session
        else
          res.error!
        end

        @servers = {}
        @eob     = {}
        @buffers = {}
      end

      def run
        buffer  = ''

        # start stream
        http = Net::HTTP.new(URI_STREAM.host, URI_STREAM.port)
        http.use_ssl = true
        http.request_get(URI_STREAM.path, 'cookie' => @session) do |response|

          p response['content-type']
          response.read_body do |str|

            buffer += str
            lines = buffer.split("\n")
            lines.each do |line|
              begin
                ev = JSON.parse line
                case ev['type']
                when 'makeserver'
                  @servers[ev['cid']] = {
                    'hostname'  => ev['hostname'],
                    'post'      => ev['port'],
                    'name'      => ev['name'] }
                  puts 'Added server: ' + ev['name']

                when 'channel_init', 'buffer_init'
                  name = ev['url'].split('/').last # hack :)
                  @buffers[ev['bid']] = {
                    'url'   => ev['url'],
                    'cid'   => ev['cid'],
                    'name'  => name }
                  puts 'Added buffer: ' + ev['url'] + ' ' + ev['bid'].to_s

                when 'end_of_backlog'
                  @eob[ev['cid']] = true

                else
                  if @eob[ev['cid']] == true and ev['highlight'] == true then
                    if buf = @buffers[ev['bid']] then
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
            end
            buffer = ''
          end
        end
      end
    end
  end
end
