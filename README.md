# Tracker Bot

**Tracker Bot** is a Discord bot designed to monitor messages for specific keywords, notify users about those keywords, and provide an array of administrative and utility features. It includes commands for managing watched words, exporting logs, setting up notifications, and more.

## Features

- **Keyword Monitoring:** Watch for specific words or phrases in messages across various channels and receive notifications when they appear.
- **Filtered Watching:** Add channel-specific filters to monitor words only in selected channels.
- **Cooldown Settings:** Set a cooldown period for alerts to prevent spam.
- **Historical Analysis:** Fetch and analyze historical messages within a specified date range.
- **Log Export:** Export message logs containing monitored keywords to an Excel file for a defined date range.
- **Role-Based Permissions:** Assign specific roles permission to use certain commands.
- **Admin Dashboard:** Access a dashboard for managing the bot's settings.
- **Notification Management:** Add or remove users to a notification list for specific keywords.
- **DM Cleanup:** Clear the bot's previous DM messages to declutter your inbox.
- **Data Management:** Save, force save, and clear all data and logs for the bot.
- **Embedded Help Command:** Use the embedded help command to get detailed documentation of all available commands directly in Discord.

## Command List

### General Commands
- **..help:** Displays detailed help documentation for all commands.
- **..watched:** Shows all words or phrases you are currently monitoring.
- **..watchword `<word>` `<channels>`:** Starts monitoring a word or phrase. Optionally specify channels for targeted monitoring.
- **..deleteword `<word>`:** Stops monitoring the specified word and clears all associated logs.
- **..watchclear:** Removes all words from your watch list and clears all logs.
- **..cd `<minutes>`:** Sets a cooldown period for alerts to avoid spamming notifications. Defaults to 15 minutes if no time is specified.
- **..worddetail `<word>`:** Provides detailed information about a watched word, including where it is being monitored.
- **..addfilter `<word>` `<channels>`:** Adds channel-specific filters to a watched word, allowing you to monitor the word only in selected channels.
- **..deletefilter `<word>` `<channels>`:** Removes channel-specific filters from a watched word.
- **..clearfilter `<word>`:** Removes all channel filters from a watched word, making it monitored in all channels.
- **..fetchhistory `<start_date>` `<end_date>` `<channels>`:** Retrieves historical messages within a specified date range for analysis. This can be limited to specific channels.
- **..exportlogs `<start_date>` `<end_date>`:** Exports logs of all detected words within a specified date range to an Excel file.
- **..checkname:** Displays the nickname and display name of the user who invokes the command. Useful for verification and administrative tasks.
- **..addnotify `<word>` `<members>`:** Adds members to the notification list for a watched word.
- **..removenotify `<word>` `<members>`:** Removes members from the notification list for a watched word.
- **..cleardm:** Clears all messages sent by the bot in your DM channel.

### Admin Commands
- **..forcesave:** Immediately saves all current data to the server. This is restricted to administrators only.
- **..botstop:** Safely shuts down the bot and saves all data. Restricted to administrators only.
- **..admindashboard:** Displays the Admin Dashboard with settings and statistics for the bot.
- **..addrole `<command>` `<role>`:** Adds a role to the permission list for a specific command, allowing users with that role to execute the command. Admin only.
- **..removerole `<command>` `<role>`:** Removes a role from the permission list for a specific command, preventing users with that role from executing the command. Admin only.
- **..listwatched:** Lists all watched words and the users watching them. Shows user details alongside the words they are monitoring. Admin only.
- **..setscan `<seconds>`:** Adjusts the frequency at which the bot scans messages. Specify the time in seconds. Admin only.
- **..setsave `<minutes>`:** Adjusts the frequency at which the bot saves data to the server. Specify the time in minutes. Admin only.
- **..clearlogs:** Clears all message logs and exported Excel files. Admin only.

### Utility Commands
- **..setverbosity `<level>`:** Sets the verbosity level of the bot's console output. Levels include 'debug', 'info', 'warning', and 'error'.
- **..test_save:** Test command to save data and check the JSON files.

## Setup and Configuration

To set up and run Tracker Bot:

1. Clone the repository.
2. Install the required dependencies using `pip`:
   ```bash
   pip install -r requirements.txt


3. Create a Discord Bot Token:
   Go to the Discord Developer Portal.
   Create a new application.
   Navigate to the "Bot" tab and add a bot to your application.
   Copy the bot token and replace the placeholder token in your code.
   
4. Running the Bot: Run the bot with the following command:
   python main.py
   Ensure you replace main.py with the filename of your bot's script if different.
   
5. **Usage:

   Invite the bot to your Discord server using the OAuth2 URL generator in the Discord Developer Portal.
   Use the prefix .. to interact with the bot. For example, ..help to see all available commands.**

6. Additional Information
   Data Files: The bot saves its data in JSON format. Ensure that the bot has write permissions to the directory where it's running.
   Permissions: Some commands are restricted to administrators only. Make sure the bot has the necessary permissions in your Discord server.
   