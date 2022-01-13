# Binary Tryant SMS Chore Bot

Just add Twilio: A roomate chore bot with SMS reminders and abscence handling

## How to Use
- Sign up to get an SMS enabled phone number from [Twilio](www.twilio.com)
- Set the roommates and thier phone numbers in roomies.json
- Set the chore order in `roomies_order.json` like `"current_roomie":"next_roomie"`
- Fill out the .env with your Twilio account SID, account API, and account SMS enabled phone number
- Set any roomate abscences in `roomies_absences.csv`, the file assumes an inclusive abscence range - this will remove the absent roomies from the order while absent
- Add the following line to the crontab of an always-on Rasberry Pi, Linode, or other high-uptime Unix machiene
```
5 * * * * <python3 interperter path> <repo_absolute_path/Driver.py> <repo_absolute_path/out.txt> 2>&1
```
- As roommate abscences come up, keep `roomies_absences.csv` up to date
