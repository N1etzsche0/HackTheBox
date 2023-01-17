var express = require('express');
var router = express.Router();
var serialize = require('node-serialize');
/* GET home page. */
router.get('/', function(req, res, next) {

//app.get('/', function(req, res){
//var result = req.query.exp
 if (req.cookies.profile) {
  var str = Buffer.from(req.cookies.profile,'base64').toString();
  var obj = serialize.unserialize(str);
  var user = obj.username
  var admin = obj.admin
console.log("Logon------------------>"+obj.logon)
  var evil = obj.logon
  var daten = Date.now()
  var evil = (daten-evil)/1000
};

  res.render('index', { title: 'WindCorp', result: user,admin: admin, evil: parseInt(evil) });
});

module.exports = router;
