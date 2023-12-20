# elf

Sample util script for integration testing the registration of users
```
rm db.sqlite
python

import csv
from round import Round

with open("sample_users.csv", "r") as f_obj:
    reader = csv.reader(f_obj)
    rows = [row for row in reader]
    
header, users = rows[0], rows[1:]

round = Round()
round.register_users(users)
```

Sample util script for making pairs
```
python

from round import Round

round = Round()
round.make_pairs()
```

Sample util script for recording wishes
```
python

from round import Round
round = Round()
wishes = ["socks", "coal", "dentistry set"]
links = [None, None, None]
round.record_wishes("bob@gmail.com", wishes, links)
```

Sample util script for getting user
```
python 

from round import Round
round = Round()
result = round.get_user("alice@gmail.com")
print(result)
```

## TODO
- Only one item is mandatory; all links are mandatory
- Looser link validation
- Revisit first-time PW setting, I don't think it's working
- Function to send a mail blast with temp credentials
- Function to send email reminder to fill out your stuff
- Function to send an account recovery PW
- Implement account recovery endpoint
- `is_admin` in data model
- admin-only endpoint to send a beginning-of-round email blast
- admin-only functionality to (re-)initialize, using previous recipients
- admin-only functionality to esport pairs after the round is over
- Styling