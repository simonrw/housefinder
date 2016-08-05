# housefinder

For finding houses using Zoopla.

Inspired by [this blog post][1], this repository queries the [Zoopla] API to
find houses. I have generalised the code to allow a custom search area, along
with inputing your own api keys.

The code inserts listings into a `postgres` database for further querying later
on, and for de-duplication of listings.

## Plan

The plan is to post the listings to [Trello] so my wife and I can discuss
together. At the moment it posts to a slack channel, but neither of us use
slack.

## Requirements

* Python 3
* `requests`
* `sqlalchemy`
* `psycopg2`

A postgres database owned by the current user account called `housefinder`.

## Running

Copy the `config.cfg.example` file to `config.cfg` and fill out the details.
You can get a Zoopla api key if you create an account with them, and [visit
your account settings page][2]. You can get a slack api key if you [add a bot
user][3] to your organisation. Finally a Trello api key can be generated [using
their developer documentation][4].

Install the package with

```sh
pip install git+https://github.com/mindriot101/housefinder.git
```

and run the command `housefinder -c <config>`.


[1]: https://www.dataquest.io/blog/apartment-finding-slackbot/
[Zoopla]: http://www.zoopla.co.uk/
[Trello]: https://trello.com/
[2]: http://developer.zoopla.com/apps/mykeys
[3]: https://api.slack.com/bot-users
[4]: https://developers.trello.com/
