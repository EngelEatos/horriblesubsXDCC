from Naked.toolshed.shell import execute_js
from subprocess import call

json = '{"todo":[{"botname" : "CR-RALEIGH|NEW","package": 5,"folder": "/home/chaos/output/"},{"botname" : "CR-RALEIGH|NEW","package": 160,"folder": "/home/chaos/output/test/"}]}';

#success = execute_js('irc-client.js', json)
#print(success)
call(["node", "irc-client2.js", json])
