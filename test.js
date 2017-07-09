var str = '{"todo":[{"botname" : "CR-RALEIGH|NEW","package": 1,"folder": "D:/output/"},{"botname" : "CR-RALEIGH|NEW","package": 2,"folder": "D:/output/"}]}';
download(str);

function download(json){
  var obj = JSON.parse(json);
  var todo = obj['todo'];
  for(var i in todo){
    var task = todo[i];
    var bot = task['botname'];
    var pkg = task['package'];
    var folder = task['folder'];
    console.log(bot + " - " + pkg  + " - " + folder);
  }
}
