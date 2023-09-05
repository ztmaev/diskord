import asyncio
import datetime
import json
import platform

import discord
import pytz
from colorama import Fore, Style, Back
from discord.ext import commands

with open("config.json") as f:
    config = json.load(f)
token = config["token"]
try:
    diskord_channel_id = config["diskord_channel_id"]
    webhook_url = config["webhook_url"]

    print(webhook_url, diskord_channel_id)
except KeyError:
    diskord_channel_id = " "
    webhook_url = " "
    with open("config.json", "r") as f:
        config = json.load(f)
        config["diskord_channel_id"] = diskord_channel_id
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.datetime.now(gmt_plus_3).strftime("%d/%m/%y %H:%M:%S")
    current_time = (Back.BLACK + Fore.GREEN + current_time + Back.RESET + Fore.WHITE + Style.BRIGHT)
    return current_time


# time in gmt+3
utc_time = datetime.datetime.utcnow()
gmt3_time = utc_time + datetime.timedelta(hours=3)
gmt3_time_full = (Back.BLACK + Fore.GREEN + gmt3_time.strftime(
    "%d/%m/%y %H:%M:%S") + Back.RESET + Fore.WHITE + Style.BRIGHT)


def generate_channel_id():
    # check for channel named diskord in category named automated
    for guild in client.guilds:
        for category in guild.categories:
            if category.name == "Automated":
                for channel in category.channels:
                    if channel.name == "diskord":
                        diskord_channel_id = channel.id
                        with open("config.json", "r") as f:
                            config = json.load(f)
                            config["diskord_channel_id"] = diskord_channel_id
                        with open("config.json", "w") as f:
                            json.dump(config, f, indent=4)
                        return diskord_channel_id


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('/', ';'), intents=discord.Intents.all())

        self.cogslist = ["cogs.tests", "cogs.help", "cogs.setup", "cogs.mod"]

    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    # on ready
    async def on_ready(self):
        print(f"{gmt3_time_full} Logged in as {Fore.CYAN + self.user.name}")
        print(f"{gmt3_time_full} Bot ID: {Fore.CYAN + str(self.user.id)}")
        print(f"{gmt3_time_full} Discord.py version: {Fore.CYAN + discord.__version__}")
        print(f"{gmt3_time_full} Python version: {Fore.CYAN + platform.python_version()}")
        print(
            f"{gmt3_time_full} Connected to {Fore.CYAN + str(len(self.guilds))} servers [{str(len(set(self.get_all_members())))} users]")

        # check for channel named diskord in category named automated
        is_channel = False
        is_webhook = False

        for guild in self.guilds:
            for category in guild.categories:
                if category.name == "Automated":
                    for channel in category.channels:
                        if channel.name == "diskord":
                            is_channel = True
                            break
                        else:
                            break

        # check for webhook
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.name == "diskord":
                    webhooks = await channel.webhooks()
                    if len(webhooks) > 0:
                        is_webhook = True
                        break

        # print status
        if is_channel:
            print(f"{current_time()}{Fore.BLUE} CONFIG:{Fore.GREEN} Channel exists" + Fore.RESET)
        else:
            print(f"{current_time()}{Fore.BLUE} CONFIG:{Fore.RED} Channel not found" + Fore.RESET)
        if is_webhook:
            print(f"{current_time()}{Fore.BLUE} CONFIG:{Fore.GREEN} Webhook exists" + Fore.RESET)
        else:
            print(f"{current_time()}{Fore.BLUE} CONFIG:{Fore.RED} Webhook not found" + Fore.RESET)

        # startup extras
        if is_channel:
            generate_channel_id()
            print(f"{current_time()}{Fore.BLUE} CONFIG:{Fore.YELLOW} Generating channel id" + Fore.RESET)

            channel_id_local = generate_channel_id()
            # get all webhooks for the channel
            channel = self.get_channel(channel_id_local)

            webhooks = await channel.webhooks()
            # first webhook
            webhook = webhooks[0]

            with open("config.json", "r") as f:
                config = json.load(f)
                config["webhook_url"] = webhook.url
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)

        if not is_webhook:
            # create empty entry to config.json
            with open("config.json", "r") as f:
                config = json.load(f)
                config["webhook_url"] = webhook_url
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)

        synced = await self.tree.sync()
        print(f"{gmt3_time_full}{Fore.YELLOW} {str(len(synced))} slash commands synced" + Fore.RESET)

        # create a status that changes every 10 seconds
        # loop
        while True:
            # status 1
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                 name=f"/help | {len(self.guilds)} servers"))
            await asyncio.sleep(10)
            # status 2
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=f"/help | {len(self.users)} users"))
            await asyncio.sleep(10)
            # status 3
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                 name=f"/help | {str(len(synced))} commands"))
            await asyncio.sleep(10)


client = Client()
client.run(token)
