db = db.getSiblingDB('$db_name');
db.createCollection('$collection_media_name');
db.createCollection('$collection_users_name');
db.createCollection("$collection_config_name")

// users
db.$collection_users_name.createIndex({"username": 1}, {unique: true});
db.$collection_users_name.createIndex({"instagram_id": 1}, {unique: true});

// media
db.$collection_media_name.createIndex({"shortcode": 1}, {unique: true});
db.$collection_media_name.createIndex({"instagram_id": 1}, {unique: true});

// tag selection strategy
db.$collection_config_name.insert({
    "type":"strategy_select_random_tag",
    "tags":$tag_list
})

// liking strategy


// follow strategy


// unfollow strategy
