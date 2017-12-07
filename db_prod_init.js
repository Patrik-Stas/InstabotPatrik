db = db.getSiblingDB('instabot');
db.createCollection('media');
db.createCollection('users');
db.createCollection("config")

// users
db.users.createIndex({"username": 1}, {unique: true});
db.users.createIndex({"instagram_id": 1}, {unique: true});

// media
db.media.createIndex({"shortcode": 1}, {unique: true});
db.media.createIndex({"instagram_id": 1}, {unique: true});

// tag selection strategy
db.config.insert({
    "type":"strategy_select_random_tag"
    "tags":["praha","tagsareawesome","prod_environment_tag","#힌국말","ывплывло","dobrý děňôčik ľoŕa"]
})

// liking strategy


// follow strategy


// unfollow strategy
