# InstabotPatrik
Awesome instagram automation! Let the bot Patrik work for you.

## Dependencies:
Python 3.6.0
MongoDB (v3.4.9)

## Run bot
Run `./bootstrap.py --help` to get help.

## Run tests
- Run `invoke test-local` to run tests which are not communicating with
Instagram (unit tests and DB integration). This also generated coverage
report.
- Run `invoke show-coverage` to display coverage in browser (for OSX)
- Run `invoke test-all` to run all tests. Generates coverage.
- Run `invoke test-api` to run API integration tests.

- Run `invoke generate-db-init` to generate init DB scripts
for production and e2e testing.
- Run `invoke init-db` to initialize production database.
- Run `invoke clean-db` to drop production database.




## TODO:
- Bot should consider people who have private profiles and follow
requests have to be be approved by the user.
- Bot could give multiple likes at once (real-life situation when you
open up someone's profile and you like the thumbnails, you take a look
at couple of them and give some likes). But keep in mind not to flood
a person with likes...liking every single picture over time...