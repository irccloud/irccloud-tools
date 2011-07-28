# -*- encoding: utf-8 -*-
$:.push File.expand_path("../lib", __FILE__)
require "irccloud-notifier/version"

Gem::Specification.new do |s|
  s.name        = "irccloud-notifier"
  s.version     = Irccloud::Notifier::VERSION
  s.authors     = ["Richard Jones"]
  s.email       = ["rj@metabrew.com"]
  s.homepage    = "https://github.com/RJ/irccloud-tools"
  s.summary     = %q{Growl Notifier for IRCCloud}
  s.description = %q{Growl Notifier for IRCCloud}

  s.rubyforge_project = "irccloud-notifier"

  s.files         = `git ls-files`.split("\n")
  s.test_files    = `git ls-files -- {test,spec,features}/*`.split("\n")
  s.executables   = `git ls-files -- bin/*`.split("\n").map{ |f| File.basename(f) }
  s.require_paths = ["lib"]

  s.add_dependency('getopt')
  s.add_dependency('ruby-growl')
end
