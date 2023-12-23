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
- Please don't share your username + password with anyone, as these are meant
to keep things *secret*

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
Dear {name:s},

This is a friendly reminder to log in and submit your wishes for this year's
Secret Santa!  Sombody has been paired with you, but they're waiting for you
to submit your wish list so that they can begin their elfing.

You should have previously received an email with your username and temporary password that you can
use to log in.

If you've already logged in for the first time, but can't remember your password,
you can reset your password using the following link:
localhost:5000/account_recovery_request

Happy Elfing!

Signed,
MoodyElfBot
""".strip()

account_recovery_subject_line = "Recover your account!"
account_recovery_message = """
Dear {name:s},

I received a request to reset your password.  If this was you, please visit the following
link to reset your password.  Please don't share this link with anybody, as it is meant
to help keep this a *Secret* Santa.

If you didn't request a password reset, please ignore this email.

This reset link will expire in 1 hour.

Link: localhost:5000/confirm_email/{token:s}

Happy Elfing!

Signed,
MoodyElfBot
""".strip()
