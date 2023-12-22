kickoff_subject_line = "Kicking things off!"
kickoff_message = """
This is the kickoff message!

Please log in using this link: localhost:5000/confirm_email/{token:s}
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
