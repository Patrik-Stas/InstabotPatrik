db = db.getSiblingDB('instabotpat');
db.createCollection('media');
db.createCollection('users');

db.users.createIndex({"username": 1}, {unique: true});
db.users.createIndex({"instagram_id": 1}, {unique: true});
db.media.createIndex({"shortcode": 1}, {unique: true});
db.media.createIndex({"instagram_id": 1}, {unique: true});
