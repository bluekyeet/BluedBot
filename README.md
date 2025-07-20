# BluedBot
## A powerful client panel for Pelican Panel all in a Discord bot.

BluedBot is a Discord bot built for being a client panel for [Pelican Panel](https://github.com/pelican-dev/panel). Built on Python with usablity on mind!

## Features
- Resource system 
-- Default resources
-- Additional resources
- Coins (Linkvertise earning, away)
-- Linkvertise
-- Gifting coins
-- Shop for resources
- Renewal system
-- Automatic checking
-- Costs coins to renew
- Servers system
-- Create servers
-- View server information
-- Edit server details
-- Delete servers
- Account system
-- Create account
-- View account details
- Admin/moderation
-- Blacklisting user from usage of bot (requires for user to be already signed up to bot.)
-- Adding coins and resources to an user
- Node/egg system
-- Easy to add and edit details
-- Easy to add limits of each thing

Post an [issue](https://github.com/bluekyeet/BluedBot/issues) if any bugs occur.
Join our [Discord server](https://discord.gg/SdyRkZ5HQM) for support!

## Installation
BluedBot requires Python 3.12 to run.

Install the requirements and create the .env file with the .example.env
```sh
pip install -r requirements.txt
cp .example.env .env
```
Edit the .env file and the nodes/eggs folders.

***NOTE: IF YOU WANT LINKVERTISE TO WORK MAKE SURE TO CREATE A REVERSE PROXY IN NGINX OR YOUR WEBSERVER TO THE SPECIFIED PORT IN THE CONFIG***
