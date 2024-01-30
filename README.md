# Auto clean bot

A really basic auto cleaner, based on rosaqq/pymod, but heavily simplified

Commands
```
cc start <id> <id>...
cc stop <id> <id>...
```
Pass the user ID of a bot you want to target for auto-clean
You can pass multiple user IDs or just one
Atm prefixes are hardcoded to . - ! so it won't clean unless you use one of these to command your bot
Has persistence and supports cleaning multiple bots at the same time

Requires a secret.json file locally - example:
```
{
  "token": "asdf",
  "autoclean_user_ids": [
    999
  ],
  "admins": [
    112,
    113
  ],
  "bot_triggers": [
    ".", "!", "-"
  ]
}
```