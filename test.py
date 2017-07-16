import json

json_data = '{"Ginpachi-Sensei" : [1123,80], "CR-RALEIGH|NEW" : [5]}'
j = json.loads(json_data)
for botname in j:
    print(botname)
    print(j[botname])
