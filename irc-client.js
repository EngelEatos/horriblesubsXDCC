//irc.rizon.net #horriblesubs Botname packageNr, downloadDir
var server = "irc.rizon.net";
var port = 6667;
var channel = "#horriblesubs";

//
var irc = require('xdcc').irc;
var ProgressBar = require('progress');
var progress, arg = process.argv;

var user = 'user_' + Math.random().toString(36).substr(2);
var bar = 'Downloading... [:bar] :percent, :etas remaining';
var client = new irc.Client(server, user, { channels: [ channel ], userName: user, realName: user });
var last = 0, handle = received => { progress.tick(received - last); last = received; };

client.on('join', (channel, nick) => nick == user && download(client, arg[2]));
client.on('xdcc-connect', meta => progress = new ProgressBar(bar, {incomplete: ' ', total: meta.length, width: 40}));
client.on('xdcc-data', handle).on('xdcc-end', r => { handle(r); process.exit(); } ).on('error', m => console.error(m));

function download(client, json){
  var obj = JSON.parse(json);
  var todo = obj['todo'];
  for(var i in todo){
    var task = todo[i];
    var bot = task['botname'];
    var pkg = task['package'];
    var folder = task['folder'];
    client.getXdcc(bot, 'xdcc send #' + pkg, folder);
  }
}
