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