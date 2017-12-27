# InstabotPatrik
Awesome instagram automation! Let the bot Patrik work for you.

# Prepare configuration
## Install dependencies:
- Python 3.6.0
- MongoDB (v3.4.9)

## Prepare configuration file
Example:
```
[database]
db_host = localhost
db_port = 27017
db_name = instabot_acc1
db_collection_users = users
db_collection_media = media
db_collection_config = config

[instagram]
username = <value>
password = <value>
```

## Initialize DB
- Prepare vars-file with definition of variables to be interpolated into
template.
- Generate db-init file
`invoke generate-db-init --template-file db_init.template.js --var-file prague.vars.json --target-file prague.init.js`
- Initialize your Mongo instance. Given our init file is `prague.init.js`:
```mongo --host localhost --port 27017 prague.init.js```

# Run bot
- Run `./bootstrap.py --help` to get help.
- Make sure your .ini configuration is matching name of DB/collections
in DB-initialization file
- Run `./bootstrap.py --config <path to .ini configuration>`

# Testing
- Run `invoke test-local` to run tests which are not communicating with
Instagram (unit tests and DB integration). This also generated coverage
report.
- Run `invoke show-coverage` to display coverage in browser (for OSX)
- Run `invoke test-all` to run all tests. Generates coverage.
- Run `invoke test-api` to run API integration tests.

- Run `invoke generate-db-init` to generate init DB scripts
for production and e2e testing.
- Run `invoke init-db` to initialize production database.


# TODO:
- Bot should consider people who have private profiles and follow
requests have to be be approved by the user.
- Bot could give multiple likes at once (real-life situation when you
open up someone's profile and you like the thumbnails, you take a look
at couple of them and give some likes). But keep in mind not to flood
a person with likes...liking every single picture over time...
