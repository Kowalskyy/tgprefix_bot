requires aiogram 2.25.1 and aiofiles
```
pip install aiogram==2.25.1 aiofiles
```
then add your token and trusted ids, and you all set.

try to add someone with it with /addprefix, or make a db with /updbd, then delete all prefixes from users, and do /reset.

# user commands
- /prefix - changes user prefix
- /restore - restores user prefix incase he left or something

# admin commands
- /addprefix - adds prefix for user, if no arguments will be passed, prefix is gonna be admin
- /delprefix - deletes prefix from user
- /updbd - creates an json file with everyone who have prefix, but has no access for admin things
- /reset - adds everyone who is in db file
