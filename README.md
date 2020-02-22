# Description
This is the first version of my telegram bot which allows a simple expenses tracker.

The bot can now take income and outcome and display the current month resume; here is a list of commands:
* `/listoutcome` print the list of current month outcome
* `/listincome` print the list of current month income
* `/delete +/-<income/outcome amount> <comment>` delete the specified entry
* `/balance` print total income, total outcome and the difference between those 2 (aka balance)
* `/income <income amount> <comment>` add to the income table the amount and the comment associated
* `/outcome <outcome amount> <comment>` add to the outcome table the amount and the comment associated

## Installation
* First create the `master.txt`  and `token.txt` files, filled respectively with your master chat id 
    and telegram bot token
* `Install docker`
* Go into the clone folder and run `docker build moneytrakerBot/`
* Copy the container id
* Run `docker run <container id>`
