import discord
from discord.ext import commands
import asyncio
import json
import os
import datetime
from collections import defaultdict
import re
import pandas as pd  # Import pandas for Excel export
from bot_token import token
import help_str
import os
import glob

# Global verbosity level
global_verbosity = 'info'

# Define the bot prefix and intents
prefix = ".."
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable members intent to access display names

def safe_print(*args, level='info'):
    """Prints safely with a verbosity level check."""
    verbosity = {
        'debug': 0,  # Most verbose, everything gets printed
        'info': 1,   # Default behavior, normal messages
        'warning': 2,  # Important non-error messages
        'error': 3,  # Critical errors only
    }
    # Use global verbosity level if bot is not defined yet
    current_verbosity = global_verbosity
    if 'bot' in globals():
        current_verbosity = getattr(bot, 'verbosity_level', 'info')
    
    if verbosity[level] >= verbosity[current_verbosity]:
        try:
            print(*args)
        except UnicodeEncodeError:
            print(*(str(arg).encode('ascii', 'ignore').decode('ascii') for arg in args))

class WordWatchBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbosity_level = 'info'  # Default verbosity level
        global global_verbosity
        global_verbosity = self.verbosity_level  # Update the global verbosity
        self.prefix = prefix
        self.user_words_file = "userwords.json"
        self.user_cds_file = "usercds.json"
        self.message_log_file = "message_log.json"
        self.thumb = "https://raw.githubusercontent.com/pixeltopic/WordWatch/master/alertimage.gif"
        self.static = -1
        self.scan_frequency = 5
        self.save_frequency = 900
        self.user_words = {}
        self.user_cds = {}
        self.message_log = defaultdict(lambda: defaultdict(list))
        self.last_checked = -1

    async def setup_hook(self):
        safe_print("Setup hook invoked. Starting save task.", level='info')
        self.save_task = asyncio.create_task(self.save_json())

    async def on_ready(self):
        safe_print(f"Logged in as {self.user.name}", level='info')
        if os.path.isfile(self.user_words_file) and os.path.isfile(self.user_cds_file) and os.path.isfile(self.message_log_file):
            with open(self.user_words_file, "r", encoding='utf-8') as word_data:
                self.user_words = json.load(word_data)
            with open(self.user_cds_file, "r", encoding='utf-8') as cd_data:
                self.user_cds = json.load(cd_data)
            with open(self.message_log_file, "r", encoding='utf-8') as log_data:
                self.message_log = json.load(log_data)
            safe_print("Data loaded successfully.", level='info')
        else:
            safe_print("No data files provided or one was missing. No user data loaded.", level='warning')
        await self.change_presence(activity=discord.Game(name=f"Questions? Type {self.prefix}help"))

    async def save_json(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(self.save_frequency)
            self.write_to_json()

    def write_to_json(self):
        try:
            safe_print("Saving user data...", level='info')
            with open(self.user_words_file, "w", encoding='utf-8') as word_file:
                json.dump(self.user_words, word_file, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)
            with open(self.user_cds_file, "w", encoding='utf-8') as cds_file:
                json.dump(self.user_cds, cds_file, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)
            with open(self.message_log_file, "w", encoding='utf-8') as log_file:
                json.dump(self.message_log, log_file, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)
            safe_print(f"User data saved at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", level='info')
        except Exception as e:
            safe_print(f"Error writing to JSON: {e}", level='error')

    def export_logs_to_excel(self, start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
        logs = []
        for date_str, channels in self.message_log.items():
            log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= log_date <= end_date:
                for channel_id, messages in channels.items():
                    for message in messages:
                        logs.append({"Date": date_str, "Channel": channel_id, "Author": message["author"], "Content": message["content"], "Timestamp": message["timestamp"]})
        df = pd.DataFrame(logs)
        file_path = f"message_logs_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
        df.to_excel(file_path, index=False, engine='xlsxwriter')
        return file_path

# Create an instance of the bot
safe_print("Creating WordWatchBot instance.")
bot = WordWatchBot(command_prefix=prefix, intents=intents, member_cache_flags=discord.MemberCacheFlags.all())

# Remove the default help command
safe_print("Removing default help command.")
bot.remove_command('help')

# Test command to verify bot command processing
@bot.command()
async def test(ctx):
    """A simple test command to check if the bot is processing commands."""
    safe_print("test command invoked")  # Debug print
    await ctx.send("Test command executed successfully!")

# Set verbosity
@bot.command()
async def setverbosity(ctx, level: str):
    """Sets the verbosity level of the bot."""
    valid_levels = ['debug', 'info', 'warning', 'error']
    if level in valid_levels:
        bot.verbosity_level = level
        await ctx.send(f"Verbosity level set to {level}.")
    else:
        await ctx.send("Invalid verbosity level. Choose from 'debug', 'info', 'warning', 'error'.")

# Define the help command
@bot.command()
async def help(ctx, page: int = 1):
    """Provides help information for available commands. Pages divide commands into manageable sections."""
    safe_print("help command invoked")  # Debug print
    if page == 1:
        embed = discord.Embed(title="Tracker Bot Commands - Page 1", description="List of available commands (1/2):", color=0x30abc0)
        embed.add_field(name="watched", value=help_str.watched_str, inline=False)
        embed.add_field(name="watchword", value=help_str.watchword_str, inline=False)
        embed.add_field(name="deleteword", value=help_str.deleteword_str, inline=False)
        embed.add_field(name="watchclear", value=help_str.watchclear_str, inline=False)
        embed.add_field(name="cd", value=help_str.cd_str, inline=False)
        embed.add_field(name="worddetail", value=help_str.worddetail_str, inline=False)
        embed.add_field(name="addfilter", value=help_str.addfilter_str, inline=False)
        embed.add_field(name="deletefilter", value=help_str.deletefilter_str, inline=False)
        embed.add_field(name="clearfilter", value=help_str.clearfilter_str, inline=False)
        embed.add_field(name="fetchhistory", value=help_str.fetchhistory_str, inline=False)
        embed.add_field(name="exportlogs", value=help_str.exportlogs_str, inline=False)
        embed.add_field(name="forcesave", value=help_str.forcesave_str, inline=False)
        embed.add_field(name="botstop", value=help_str.botstop_str, inline=False)
    elif page == 2:
        embed = discord.Embed(title="Tracker Bot Commands - Page 2", description="List of available commands (2/2):", color=0x30abc0)
        embed.add_field(name="admindashboard", value=help_str.admindashboard_str, inline=False)
        embed.add_field(name="addrole", value=help_str.addrole_str, inline=False)
        embed.add_field(name="removerole", value=help_str.removerole_str, inline=False)
        embed.add_field(name="listwatched", value=help_str.listwatched_str, inline=False)
        embed.add_field(name="setscan", value=help_str.setscan_str, inline=False)
        embed.add_field(name="setsave", value=help_str.setsave_str, inline=False)
        embed.add_field(name="checkname", value=help_str.checkname_str, inline=False)
        embed.add_field(name="addnotify", value=help_str.addnotify_str, inline=False)
        embed.add_field(name="removenotify", value=help_str.removenotify_str, inline=False)
        embed.add_field(name="test_save", value=help_str.test_save_str, inline=False)
        embed.add_field(name="..setverbosity", value=help_str.setverbosity_str, inline=False)
        embed.add_field(name="..cleardm", value=help_str.clear_dm_str, inline=False)
        embed.add_field(name="clearlogs", value=help_str.clearlogs_str, inline=False)
    else:
        await ctx.send("Invalid help page number.")
        return

    embed.set_footer(text=help_str.footer_str)
    await ctx.author.send(embed=embed)

# Define the watched command
@bot.command()
async def watched(ctx):
    """Gives user a list of all watched words/phrases on the server."""
    safe_print(f"watched command invoked")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        if user_id not in bot.user_words or guild_id not in bot.user_words[user_id]:
            await ctx.send(f"You have no watched words.")
            return

        watched_words = list(bot.user_words[user_id][guild_id].keys())
        await ctx.send(f"Your watched words: {', '.join(watched_words)}")
    except Exception as e:
        safe_print(f"Error in watched: {e}")  # Log error to console
        await ctx.send("An error occurred while retrieving watched words.")

# Define the watchword command
@bot.command()
async def watchword(ctx, word: str, *channels: discord.TextChannel):
    """Start watching a word or phrase in specified channels."""
    safe_print(f"watchword command invoked with word: {word} and channels: {channels}")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        if user_id not in bot.user_words:
            bot.user_words[user_id] = {}
        if guild_id not in bot.user_words[user_id]:
            bot.user_words[user_id][guild_id] = {}

        if word.lower() in bot.user_words[user_id][guild_id]:
            await ctx.send(f"Word '{word}' is already in your watch list.")
            return

        # Add the word to the user's watch list in specified channels and initialize notify_users
        bot.user_words[user_id][guild_id][word.lower()] = {
            "channels": {channel.id: bot.static for channel in channels} if channels else {},
            "last_alerted": 0,
            "notify_users": []  # Initialize notify_users as an empty list
        }
        await ctx.send(f"Word '{word}' has been added to your watch list in the specified channels.")
    except Exception as e:
        safe_print(f"Error in watchword: {e}")  # Log error to console
        await ctx.send("An error occurred while adding the word to your watch list.")

# Define the deleteword command
@bot.command()
async def deleteword(ctx, word: str):
    """Deletes the specified word from your watch list and its logs."""
    safe_print(f"deleteword command invoked with word: {word}")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        # Check if the word exists in the watch list
        if user_id not in bot.user_words or guild_id not in bot.user_words[user_id] or word.lower() not in bot.user_words[user_id][guild_id]:
            await ctx.send(f"Word '{word}' is not in your watch list.")
            return

        # Delete the word from the user's watch list
        del bot.user_words[user_id][guild_id][word.lower()]

        # Remove the word's logs from the message_log
        for date_str, channels in bot.message_log.items():
            for channel_id, messages in channels.items():
                # Remove messages that contain the word
                bot.message_log[date_str][channel_id] = [msg for msg in messages if word.lower() not in msg["content"].lower()]

        await ctx.send(f"Word '{word}' has been removed from your watch list and its logs have been cleared.")
    except Exception as e:
        safe_print(f"Error in deleteword: {e}")  # Log error to console
        await ctx.send("An error occurred while removing the word from your watch list.")

# Define the watchclear command
@bot.command()
async def watchclear(ctx):
    """Clears all watched words/phrases that you are watching."""
    safe_print("watchclear command invoked")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        if user_id in bot.user_words and guild_id in bot.user_words[user_id]:
            bot.user_words[user_id][guild_id] = {}
            await ctx.send("Your watch list has been cleared.")
        else:
            await ctx.send("You have no watched words to clear.")
    except Exception as e:
        safe_print(f"Error in watchclear: {e}")  # Log error to console
        await ctx.send("An error occurred while clearing your watch list.")

# Define the cd command
@bot.command()
async def cd(ctx, minutes: int = 15):
    """Set cooldown (in minutes) for each word. If no parameter, defaults to 15 minutes."""
    safe_print(f"cd command invoked with minutes: {minutes}")  # Debug print
    user_id = str(ctx.author.id)

    try:
        bot.user_cds[user_id] = minutes * 60  # convert minutes to seconds
        await ctx.send(f"Notification cooldown set to {minutes} minutes.")
    except Exception as e:
        safe_print(f"Error in cd: {e}")  # Log error to console
        await ctx.send("An error occurred while setting the cooldown.")

# Define worddetail command
@bot.command()
async def worddetail(ctx, word: str):
    """Provides details for a watched word."""
    safe_print(f"worddetail command invoked with word: {word}")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        if user_id not in bot.user_words or guild_id not in bot.user_words[user_id] or word.lower() not in bot.user_words[user_id][guild_id]:
            await ctx.send(f"Word '{word}' is not in your watch list.")
            return

        word_data = bot.user_words[user_id][guild_id][word.lower()]
        channels = [f"<#{channel_id}>" for channel_id in word_data["channels"]]
        last_seen = datetime.datetime.fromtimestamp(word_data["last_alerted"]).strftime('%Y-%m-%d %H:%M:%S')
        await ctx.send(f"Word '{word}' is being watched in: {', '.join(channels) if channels else 'all channels'}\nLast seen: {last_seen}")
    except Exception as e:
        safe_print(f"Error in worddetail: {e}")  # Log error to console
        await ctx.send("An error occurred while retrieving word details.")

# Define addfilter command
@bot.command()
async def addfilter(ctx, word: str, *channels: discord.TextChannel):
    """Start watching for word/phrase in specified channels."""
    safe_print(f"addfilter command invoked with word: {word} and channels: {channels}")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        if user_id not in bot.user_words:
            bot.user_words[user_id] = {}
        if guild_id not in bot.user_words[user_id]:
            bot.user_words[user_id][guild_id] = {}

        if word.lower() not in bot.user_words[user_id][guild_id]:
            await ctx.send(f"Word '{word}' is not in your watch list.")
            return

        word_data = bot.user_words[user_id][guild_id][word.lower()]
        for channel in channels:
            word_data["channels"][channel.id] = bot.static
        
        await ctx.send(f"Filters have been added to the word '{word}' for the specified channels.")
    except Exception as e:
        safe_print(f"Error in addfilter: {e}")  # Log error to console
        await ctx.send("An error occurred while adding filters to the word.")

# Define deletefilter command
@bot.command()
async def deletefilter(ctx, word: str, *channels: discord.TextChannel):
    """Stop watching for word/phrase in specified channels."""
    safe_print(f"deletefilter command invoked with word: {word} and channels: {channels}")  # Debug print
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    try:
        if user_id not in bot.user_words or guild_id not in bot.user_words[user_id] or word.lower() not in bot.user_words[user_id][guild_id]:
            await ctx.send(f"Word '{word}' is not in your watch list.")
            return

        word_data = bot.user_words[user_id][guild_id][word.lower()]
        for channel in channels:
            if channel.id in word_data["channels"]:
                del word_data["channels"][channel.id]
        
        await ctx.send(f"Filters have been removed from the word '{word}' for the specified channels.")
    except Exception as e:
        safe_print(f"Error in deletefilter: {e}")  # Log error to console
        await ctx.send("An error occurred while deleting filters from the word.")

# Define fetchhistory command
@bot.command()
async def fetchhistory(ctx, start_date: str, end_date: str, *channels: discord.TextChannel):
    """Fetch and process historical messages from specified channels in the guild within a date range."""
    safe_print(f"fetchhistory command invoked with start_date: {start_date}, end_date: {end_date}, and channels: {channels}")  # Debug print

    # Dictionary to store the notification messages to edit them later
    notification_messages = {}

    try:
        # Convert the start and end dates
        start_date_obj = datetime.datetime.strptime(start_date, "%Y%m%d")
        end_date_obj = datetime.datetime.strptime(end_date, "%Y%m%d")

        fetched_messages = 0
        # If no specific channels are provided, use all text channels in the guild
        target_channels = channels if channels else ctx.guild.text_channels

        # Iterate over the specified text channels
        for channel in target_channels:
            async for message in channel.history(limit=None):  # Fetch as many messages as possible
                user_id = str(ctx.author.id)
                guild_id = str(ctx.guild.id)

                # Ignore the bot's own messages and commands
                if message.author == bot.user or message.content.startswith(bot.command_prefix):
                    continue

                # Skip messages with unsupported sticker formats
                if message.stickers:
                    if not all(sticker.format in [discord.StickerFormatType.png, discord.StickerFormatType.apng, discord.StickerFormatType.lottie] for sticker in message.stickers):
                        continue  # Skip the message if it contains any unsupported sticker format

                # Ensure user's word list and guild exist
                if user_id not in bot.user_words or guild_id not in bot.user_words[user_id]:
                    continue

                # Check for keywords in the message and date range
                message_date = message.created_at.date()
                if start_date_obj.date() <= message_date <= end_date_obj.date():
                    for keyword, data in bot.user_words[user_id][guild_id].items():
                        # Use regex to match the whole word
                        if re.search(rf'\b{re.escape(keyword)}\b', message.content, re.IGNORECASE):
                            # Log the message grouped by date and channel
                            date_str = message.created_at.strftime('%Y-%m-%d')
                            if date_str not in bot.message_log:
                                bot.message_log[date_str] = {}
                            if str(channel.id) not in bot.message_log[date_str]:
                                bot.message_log[date_str][str(channel.id)] = []

                            # Attempt to fetch the member's display name
                            member = message.guild.get_member(message.author.id)
                            if not member:
                                member_display_name = "Unknown"  # Fallback if member is not found
                            else:
                                member_display_name = member.display_name

                            # Add message details to the log
                            bot.message_log[date_str][str(channel.id)].append({
                                "author": member_display_name,
                                "content": message.content,
                                "timestamp": message.created_at.isoformat()
                            })

                            # Notify users if set in the 'notify_users' list
                            notify_users = data.get('notify_users', [])
                            for notify_user_id in notify_users:
                                user = bot.get_user(notify_user_id)
                                if user:
                                    key = f"{notify_user_id}_{keyword}"
                                    notif_msg, count = notification_messages.get(key, (None, 0))
                                    count += 1
                                    if notif_msg:
                                        await notif_msg.edit(content=f"Keyword '{keyword}' was mentioned {count} times.")
                                    else:
                                        notif_msg = await user.send(f"Keyword '{keyword}' mentioned in {message.channel.mention}.")
                                    notification_messages[key] = (notif_msg, count)

                            fetched_messages += 1

        await ctx.send(f"Fetched and processed {fetched_messages} historical messages across the specified channels.")
    except Exception as e:
        safe_print(f"Error in fetchhistory: {e}")  # Log error to console
        await ctx.send(f"An error occurred while fetching historical messages: {e}")

# Define exportlogs command
@bot.command()
async def exportlogs(ctx, start_date: str, end_date: str):
    """Exports the message logs to an Excel file for the specified date range."""
    safe_print(f"exportlogs command invoked with start_date: {start_date}, end_date: {end_date}")  # Debug print

    try:
        # Export logs to an Excel file
        file_path = bot.export_logs_to_excel(start_date, end_date)

        # Send the file to the user
        await ctx.send(file=discord.File(file_path))
    except Exception as e:
        safe_print(f"Error in exportlogs: {e}")  # Log error to console
        await ctx.send(f"An error occurred while exporting the logs: {e}")

# Define forcesave command
@bot.command()
@commands.has_permissions(administrator=True)
async def forcesave(ctx):
    """Force saves all current data into the JSON files. Admin only!"""
    safe_print("forcesave command invoked")  # Debug print
    try:
        bot.write_to_json()
        await ctx.send("All data has been force-saved to the JSON files.")
    except Exception as e:
        safe_print(f"Error in forcesave: {e}")  # Log error to console
        await ctx.send("An error occurred while force-saving data.")

# Define checkname command
@bot.command()
async def checkname(ctx):
    """Check the nickname and display name of the command invoker."""
    member = ctx.guild.get_member(ctx.author.id)
    if member:
        await ctx.send(f"Display Name: {member.display_name}, Nickname: {member.nick if member.nick else 'No Nickname'}")
    else:
        await ctx.send(f"Unable to fetch member from cache.")

# Define botstop command
@bot.command()
@commands.has_permissions(administrator=True)
async def botstop(ctx):
    """Saves data and logs out bot. Admin only!"""
    safe_print("botstop command invoked")  # Debug print
    try:
        await ctx.send("Saving data and logging out...")
        bot.write_to_json()
        await bot.close()
    except Exception as e:
        safe_print(f"Error in botstop: {e}")  # Log error to console
        await ctx.send("An error occurred while stopping the bot.")

# Define admindashboard command
@bot.command()
@commands.has_permissions(administrator=True)
async def admindashboard(ctx):
    """Displays the Admin Dashboard for managing the bot settings."""
    # Create the embed for the dashboard
    embed = discord.Embed(title="WordWatch Bot Admin Dashboard", color=0x3498db)
    embed.set_thumbnail(url=bot.thumb)
    embed.add_field(name="Scan Frequency", value=f"{bot.scan_frequency} seconds", inline=False)
    embed.add_field(name="Save Frequency", value=f"{bot.save_frequency / 60} minutes", inline=False)
    embed.add_field(name="Watched Words", value=f"{len(bot.user_words)} users", inline=False)
    embed.add_field(name="Commands", value=(
        "`..setscan <seconds>` - Set scan frequency\n"
        "`..setsave <minutes>` - Set save frequency\n"
        "`..listwatched` - List all watched words"
    ), inline=False)
    embed.set_footer(text="Use the commands to modify settings.")

    await ctx.send(embed=embed)

# Command to set the scan frequency
@bot.command()
@commands.has_permissions(administrator=True)
async def setscan(ctx, seconds: int):
    """Sets the scan frequency in seconds."""
    if seconds < 1:
        await ctx.send("Scan frequency must be at least 1 second.")
        return
    bot.scan_frequency = seconds
    await ctx.send(f"Scan frequency set to {seconds} seconds.")

# Command to set the save frequency
@bot.command()
@commands.has_permissions(administrator=True)
async def setsave(ctx, minutes: int):
    """Sets the save frequency in minutes."""
    if minutes < 1:
        await ctx.send("Save frequency must be at least 1 minute.")
        return
    bot.save_frequency = minutes * 60  # Convert to seconds
    await ctx.send(f"Save frequency set to {minutes} minutes.")

# Command to addrole
@bot.command()
@commands.has_permissions(administrator=True)
async def addrole(ctx, command: str, role: discord.Role):
    try:
        # Ensure the file exists and is not empty
        if not os.path.exists('command_permissions.json') or os.stat('command_permissions.json').st_size == 0:
            with open('command_permissions.json', 'w') as f:
                f.write('{}')  # Write an empty JSON object
        
        with open('command_permissions.json', 'r+') as f:
            permissions = json.load(f)
            if command in permissions:
                if str(role.id) not in permissions[command]:
                    permissions[command].append(str(role.id))
                    f.seek(0)
                    f.truncate()
                    json.dump(permissions, f, indent=4)
                    await ctx.send(f"Role {role.name} added to {command}.")
                else:
                    await ctx.send("Role already has permission for this command.")
            else:
                permissions[command] = [str(role.id)]
                f.seek(0)
                f.truncate()
                json.dump(permissions, f, indent=4)
                await ctx.send(f"Role {role.name} added to {command}.")
    except json.JSONDecodeError:
        await ctx.send("There was an error reading the permissions file. Please check its format.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removerole(ctx, command: str, role: discord.Role):
    try:
        # Ensure the file exists and is not empty
        if not os.path.exists('command_permissions.json') or os.stat('command_permissions.json').st_size == 0:
            with open('command_permissions.json', 'w') as f:
                f.write('{}')  # Write an empty JSON object

        with open('command_permissions.json', 'r+') as f:
            permissions = json.load(f)
            if command in permissions and str(role.id) in permissions[command]:
                permissions[command].remove(str(role.id))
                f.seek(0)
                f.truncate()
                json.dump(permissions, f, indent=4)
                await ctx.send(f"Role {role.name} removed from {command}.")
            else:
                await ctx.send("Role was not set for this command or command does not exist.")
    except json.JSONDecodeError:
        await ctx.send("There was an error reading the permissions file. Please check its format.")

# Command to list all watched words
@bot.command()
@commands.has_permissions(administrator=True)
async def listwatched(ctx):
    """Lists all watched words and the users watching them."""
    watched_summary = ""
    for user_id, guilds in bot.user_words.items():
        user = await bot.fetch_user(user_id)
        for guild_id, words in guilds.items():
            watched_summary += f"**{user.name}** ({len(words)} words): {', '.join(words.keys())}\n"

    if watched_summary == "":
        watched_summary = "No words are being watched currently."

    # Create the embed for the watched words summary
    embed = discord.Embed(title="Watched Words Summary", description=watched_summary, color=0x3498db)
    await ctx.send(embed=embed)

# Command to remove members to the notification list
@bot.command()
async def removenotify(ctx, word: str, *members: discord.Member):
    """Removes members from the notification list for a watched word."""
    user_id = str(ctx.author.id)  # Define user_id here
    guild_id = str(ctx.guild.id)
    word = word.lower()

    if user_id in bot.user_words and guild_id in bot.user_words[user_id] and word in bot.user_words[user_id][guild_id]:
        notify_list = bot.user_words[user_id][guild_id][word].get('notify_users', [])
        removed_members = []
        for member in members:
            if member.id in notify_list:
                notify_list.remove(member.id)
                removed_members.append(member.display_name)
        if removed_members:
            await ctx.send(f"Removed {', '.join(removed_members)} from notifications for '{word}'.")
        else:
            await ctx.send("No members were removed.")
    else:
        await ctx.send(f"'{word}' is not being watched.")

# Command to add members to the notification list
@bot.command()
async def addnotify(ctx, word: str, *members: discord.Member):
    """Adds members to the notification list for a watched word."""
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)
    word = word.lower()
    
    safe_print("Current user words structure:", bot.user_words)  # Debugging line
    
    if user_id in bot.user_words and guild_id in bot.user_words[user_id] and word in bot.user_words[user_id][guild_id]:
        notify_list = bot.user_words[user_id][guild_id][word].get('notify_users', [])
        added_members = []
        
        for member in members:
            if member.id not in notify_list:
                notify_list.append(member.id)
                added_members.append(member.display_name)
        
        # Update the notify_users list
        bot.user_words[user_id][guild_id][word]['notify_users'] = notify_list
        
        if added_members:
            await ctx.send(f"Added {', '.join(added_members)} to notifications for '{word}'.")
        else:
            await ctx.send("No new members were added.")
    else:
        await ctx.send(f"'{word}' is not being watched.")

# Command to test json files
@bot.command()
async def test_save(ctx):
    """Test command to save data and check the JSON files."""
    bot.write_to_json()  # No await, since this is not an async function
    await ctx.send("Test save executed. Check the JSON files.")

# Command to clear logs
@bot.command()
@commands.has_permissions(administrator=True)
async def clearlogs(ctx):
    """Clears all the message logs and exported .xlsx files with a confirmation step."""
    # Create an embed asking for confirmation
    embed = discord.Embed(
        title="Clear All Message Logs and Exported Files",
        description="Are you sure you want to clear all message logs and exported Excel files? This action cannot be undone.",
        color=0xff0000  # Red color to signify caution
    )
    embed.set_footer(text="React with ✅ to confirm or ❌ to cancel.")
    message = await ctx.send(embed=embed)

    # React with confirmation and cancellation emojis
    await message.add_reaction('✅')
    await message.add_reaction('❌')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == message.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. Message logs and files were not cleared.")
        return
    else:
        if str(reaction.emoji) == '✅':
            # Clear the message logs in memory
            bot.message_log.clear()
            bot.write_to_json()  # Save the empty state to JSON

            # Find and remove all .xlsx files
            for file in glob.glob('*.xlsx'):
                os.remove(file)
            await ctx.send("All message logs and exported Excel files have been cleared.")
        else:
            await ctx.send("Message log and file clearance cancelled.")

# Command to clear the bots Dms
@bot.command()
async def cleardm(ctx):
    # Check if the command is in a DM
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs with the bot.")
        return

    try:
        # Retrieve the last 100 messages in the DM
        async for message in ctx.channel.history(limit=100):
            # Check if the message is from the bot
            if message.author == bot.user:
                await message.delete()
        await ctx.send("Cleared my messages from this DM.")
    except Exception as e:
        await ctx.send("An error occurred while trying to clear messages.")
        safe_print(f"Error clearing DMs: {e}", level='error')

# Global error handler to catch and log errors
@bot.event
async def on_command_error(ctx, error):
    """Global error handler."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Please check the command and try again.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the required permissions to use this command.")
    else:
        # Log other errors
        safe_print(f"Error: {error}")
        await ctx.send(f"An error occurred: {error}")

async def main():
    # Run the bot
    safe_print("Starting the bot...")  # Debug print
    await bot.start(token)

# Run the main function
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.logout())
        # cancel all tasks lingering
    finally:
        loop.close()

