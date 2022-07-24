# Description

This is the first version of my telegram bot which allows a simple expenses tracker. It is based on 
[this library](https://github.com/eternnoir/pyTelegramBotAPI) 

The bot can now take income and outcome and display the current month resume; here is a list of commands:

* `/listoutcome <month>`[^1] print the list of the chosen month outcome, if blank the current month is used
* `/listincome <month>`[^1] print the list of the chosen month income, if blank the current month is used
* `/delete +/-<income/outcome amount> <comment>` delete the specified entry
* `/balance <month>`[^1] print total income, total outcome and the difference between those 2 (aka balance)
* `/income <income amount> <comment>` add to the income table the amount and the comment associated
* `/outcome <outcome amount> <comment>` add to the outcome table the amount and the comment associated

[^1]: Month can be written according to the following example: 'Jul', 'July', '07' or '7'

## Installation

### Docker run method
* `Install docker`
* Create the `token.txt` file, filled with the telegram bot token
* Go into the clone folder and run `docker build moneytrackerBot/`
* Copy the container id
* Run `docker run <container id>`

### Docker compose method
* `Install docker`
* Create the `token.txt` file, filled with the telegram bot token
* Run `docker-compose up -d`