# Twitter Reply Bot

## Deployment Steps

1. Create new Twitter Account for your bot (Note: You should set your bot account as [managed](https://help.twitter.com/en/using-twitter/automated-account-labels) by your company or personal account)
2. Get Twitter Developer API keys from https://developer.twitter.com/en/portal/dashboard (Note: Unfortunately you'll need the basic/paid tier for this bot to work)
3. [Optional] Create an Airtable account and create a personal access token - If you don't want to use airtable you can comment out references to it in the code.
4. [Airtable] If you choose to do logging (the default option) then you'll need to create an airtable table with the [columns here](https://github.com/gkamradt/twitter-reply-bot/blob/a8854dc96539c81a6e41d88990dea2030c081ac8/twitter-reply-bot.py#LL100C4-L100C4).
5. Close this github repo
6. Create railway account to host your code (or host whereever you want)
7. Add your [environment variables](https://github.com/gkamradt/twitter-reply-bot/blob/a8854dc96539c81a6e41d88990dea2030c081ac8/twitter-reply-bot.py#L15) to a .env file, your railway app, or whereever you host your app
8. Deploy and run!
