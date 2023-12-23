kickoff_subject_line = "Kicking things off!"
kickoff_message = """
Dear {name:s},

Merry Christmas from MoodyElfBot!  It is that time of year again, which means it is
time for a round of Secret Santa!  I'm sending you this kickoff email to let you know that
this year's Secret Santa has officially started.

How it works:

You can log in using the username and temporary password below.  The first time you
log in, you'll be prompted to change your password.  Then, you'll be prompted to 
enter up to 3 wishes -- don't forget to include a URL link!  Think carefully before
submitting your wishes: once you hit the "Submit" button, you won't be able to 
modify them anymore.  Once you have submitted your wishes, you will be able to
see who you've been paired with (they won't be able to see you, of course), and
you can see what they've put on their wishlist.

The rules:

- Everybody is paired up with somebody from a different family
- Everybody is paired up with somebody other than who they Santa'd for last year
- Please keep gift totals to $50 or under
- Please don't delay in submitting your wishes -- you want to give your Secret Santa
some time to do their elfing!  

Please log in using this login information:

URL: {url:s}
Username: {email:s}
Temporary password: {password:s}
(Note: you will be asked to change your password when you first log in.)

Happy Elfing!

Signed,
MoodyElfBot
""".strip()

reminder_subject_line = "Reminding you!"
reminder_message = """
This is the reminder message!
""".strip()

account_recovery_subject_line = "Recover your account!"
account_recovery_message = """
This is the account recovery message!

Please visit this address to reset your password: localhost:5000/confirm_email/{token:s}
""".strip()
