This code allows you to basically create your own Instagram feed away from its algorithm, showing you only unseen posts from accounts that you list in "accounts.sh". Note that this comes with the caveat that it only works for *public* Instagram accounts. 

## ⚠️Warning⚠️

I highly *highly* recommend running this with a VPN or on some wireless network that you do not care about getting banned from. I have yet to be detected by Instagram when running this code, but they are notorious for cracking down on people trying to scrape their website in any form. 

## Usage

0. Install the relevant dependencies.
1. Add the Instagram usernames that you wish to add to your feed to "accounts.sh". You can comment out any line with the "#" symbol, so I recommend structuring your "accounts.sh" file with headers. For a simplistic example, see the file attached in this repository.
2. Run the code and wait for the popup. *Note that if you run the code too frequently Instagram may not show any posts for a bit. In this case, you will get a warning telling you to wait a few minutes before trying again.*
3. A popup will appear with any posts gathered from Instagram not found in your history. (Generally, this code will not gather *all* posts from the accounts you desire but rather the most recent dozen or so). You are able to click on the links and check the box next to them to indicate that you saw the post. Click "Done" to exit the program and add the posts you've selected to your history. These posts will not be shown to you again.