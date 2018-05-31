var express = require('express');
var Redis = require('ioredis');

var app = express();
var redis = new Redis({ port: 6379, host: '127.0.0.1' });


// --------------------------------
// Global Return Calls
// --------------------------------

app.get('/api/models', function(req, res) {
  // Return a list of all models available
  redis.lrange('model_names', 0, -1).then((v) => res.send(v));
})


// --------------------------------
// Model Specific Return Calls
// --------------------------------

app.get('/api/models/:model/specs', function(req, res) {
  // Return the specs for the given model
  key = req.params['model'] + ':specs';
  redis.hgetall(key).then((v) => res.json(v));
})

app.get('/api/models/:model/loss', function(req, res) {
  // Return the list of loss values for each step
  key = req.params['model'] + ':loss';
  redis.lrange(key, 0, -1).then((v) => res.send(v));
})

app.get('/api/models/:model/selective_times', function(req, res) {
  // Return the list of loss values for each step
  key = req.params['model'] + ':selective_times';
  redis.lrange(key, 0, -1).then((v) => res.send(v));
})

app.get('/api/models/:model/reward', function(req, res) {
  // Return the list of loss values for each step
  key = req.params['model'] + ':reward';
  redis.lrange(key, 0, -1).then((v) => res.send(v));
})


// --------------------------------
// Timestep Specific Return Calls
// --------------------------------

app.get('/api/models/:model/reward/:timestep', function(req, res) {
  // Return only the reward at timestep t
  t = req.params['timestep']
  key = req.params['model'] + ':reward';
  redis.lrange(key, t, t).then((v) => res.send(v));
})

app.get('/api/models/:model/action/:timestep', function(req, res) {
  // Return only the action at timestep t
  t = req.params['timestep']
  key = req.params['model'] + ':action';
  redis.lrange(key, t, t).then((v) => res.send(v));
})

app.get('/api/models/:model/screen/:timestep', function(req, res) {
  // Return the Q-estimates at timestep t
  key = req.params['model'] + ':screen:' + req.params['timestep'];
  //redis.get(key).then((v) => res.send(v));
  res.send('I am not sure this functionality is working...');
})

app.get('/api/models/:model/q_estimate/:timestep', function(req, res) {
  // Return the Q-estimates at timestep t
  key = req.params['model'] + ':q_estimate:' + req.params['timestep'];
  //redis.get(key).then((v) => res.send(v));
  res.send('I am not sure this functionality is working...');
})

app.get('/api/models/:model/q_future/:timestep', function(req, res) {
  // Return the Q-forecasts for the future at timestep t
  key = req.params['model'] + ':q_future:' + req.params['timestep'];
  //redis.get(key).then((v) => res.send(v));
  res.send('I am not sure this functionality is working...');
})


// Start the server
app.listen(3000);
