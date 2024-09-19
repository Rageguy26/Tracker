# help_str.py
# Help strings for the WordWatch Bot

# Main description
description_str = """
**Welcome to the Tracker Bot!**
This bot monitors messages for specified keywords and notifies you when they appear. 
Use the following commands to manage keywords, view logs, and configure settings.
All commands must be prefixed with '{prefix}'.
"""

# Command descriptions
watched_str = "Displays a list of all words you are currently watching."
watchword_str = "Starts monitoring a specific word or phrase in your messages. You can specify channels to narrow down the monitoring."
deleteword_str = "Stops monitoring the specified word and clears all associated logs."
watchclear_str = "Removes all words from your watch list and clears all logs."
cd_str = "Sets a cooldown period for alerts on each word to avoid spamming notifications."
worddetail_str = "Provides detailed information about a watched word, including where it is being monitored."
addfilter_str = "Adds channel-specific filters to a watched word, allowing you to monitor the word only in selected channels."
deletefilter_str = "Removes channel-specific filters from a watched word."
clearfilter_str = "Removes all channel filters from a watched word, making it monitored in all channels."
fetchhistory_str = "Retrieves historical messages within a specified date range for analysis. This can be limited to specific channels."
exportlogs_str = "Exports logs of all detected words within a specified date range to an Excel file."
forcesave_str = "Immediately saves all current data to the server. This is restricted to administrators only."
botstop_str = "Safely shuts down the bot and saves all data. Restricted to administrators only."
admindashboard_str = "Displays administrative settings and statistics for the bot."
addrole_str = "Adds a role to the permission list for a specific command, allowing users with that role to execute the command."
removerole_str = "Removes a role from the permission list for a specific command, preventing users with that role from executing the command."
listwatched_str = "Lists all watched words and the users watching them. Shows user details alongside the words they are monitoring."
setscan_str = "Adjusts the frequency at which the bot scans messages. Specify the time in seconds."
setsave_str = "Adjusts the frequency at which the bot saves data to the server. Specify the time in minutes."
checkname_str = "Displays the nickname and display name of the user who invokes the command. Useful for verification and administrative tasks."
test_save_str = "Test command to save data and check the JSON files."
addnotify_str = "Adds members to the notification list for a watched word."
removenotify_str = "Removes members from the notification list for a watched word."
setverbosity_str = "Adjusts the verbosity level of console outputs. Specify the level (`debug`, `info`, `warning`, `error`) to control the detail of logs."
clear_dm_str = "Clears all messages sent by the bot in this DM. Use with caution as this cannot be undone."
clearlogs_str = "Clears all stored message logs and deletes exported Excel files. Includes a confirmation step to prevent accidental data loss."



# Footer text
footer_str = "Ensure you have the necessary permissions to use these commands. Contact the admin for more details."
