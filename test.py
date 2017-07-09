from Naked.toolshed.shell import execute_js
from subprocess import call

json = '{"todo":[{"botname" : "CR-RALEIGH|NEW","package": 1,"folder": "D:/output/"},{"botname" : "CR-RALEIGH|NEW","package": 2,"folder": "D:/output/"}]}';

#success = execute_js('irc-client.js', json)
#print(success)
call(["node", "irc-client.js", json])
