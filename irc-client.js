// Get dependencies
var irc = require('xdcc').irc;
var ProgressBar = require('ascii-progress');
// Set IRC configuration
var user = 'engelbot';
var server = "irc.rizon.net";
var port = 6667;
var channel = "#horriblesubs";
//
var progress;
var queue = [];
var json = process.argv[2];
var hostUser;
var last = 0;

var todo = JSON.parse(json)['todo'];
for(var i in todo){
  var task = todo[i];
  queue.push(task);
}

var client = new irc.Client('irc.rizon.net', user, {
  channels: ['#horriblesubs'],
  userName: user,
  realName: user
});
console.log("-- CONNECTING");

function nextTask(){
  if (queue.length == 0) {
    client.disconnect()
    process.exit(0);
  }
  var task = queue.shift();
  last,received = 0;
  progress = null;
  hostUser = task['botname'];
  client.getXdcc(task['botname'], 'xdcc send #' + task['package'], task['folder']);
}

client.on('join', function (channel, nick, message) {
  if(nick !== user) return;
  console.log('-- Joined ' + channel);
  nextTask();
});

client.on('xdcc-connect', function(meta) {
  console.log('Downloading: ' + meta.file);
  progress = new ProgressBar({
    schema: '[:bar] :current/:total :percent :etas',
    total: meta.length,
    current: 0
  });
});

client.on('xdcc-data', function(received) {
  progress.tick(received - last);
  last = received;
});

client.on('xdcc-end', function(received) {
  received, last = 0;
  nextTask();
});

client.on('notice', function(from, to, message) {
  if (to == user && from == hostUser) {
    console.log("[notice]", message);
  }
});

client.on('error', function(message) {
  console.error(message);
});
