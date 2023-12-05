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
round.record_wishes("alice@gmail.com", wishes, links)
```

Sample util script for getting user
```
python 

from round import Round
round = Round()
result = round.get_user("alice@gmail.com")
print(result)
```