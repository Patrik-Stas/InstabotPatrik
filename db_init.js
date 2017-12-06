db = db.getSiblingDB('instabotpat');
db.createCollection('media');
db.createCollection('users');
db.createCollection("config")

db.users.createIndex({"username": 1}, {unique: true});
db.users.createIndex({"instagram_id": 1}, {unique: true});
db.media.createIndex({"shortcode": 1}, {unique: true});
db.media.createIndex({"instagram_id": 1}, {unique: true});

db.config.insert({
    "type":"strategy_select_random_tag"
    "tags":["a", "b", "c", "d", "mytags"]
})