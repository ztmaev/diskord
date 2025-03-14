import asyncio
import datetime
import json
import os
import platform
import random
import subprocess

import discord
import pytz
from colorama import Fore, Style, Back
from discord.ext import commands

from jsondb import write_to_db

# start server
server_path = "server.py"
server = subprocess.Popen(["python", server_path])

with open("config.json") as f:
    config = json.load(f)
token = config["token"]
try:
    diskord_channel_id = config["diskord_channel_id"]
    webhook_url = config["webhook_url"]

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


def generate_id():
    # random 7 character string
    uuid = ""
    for i in range(7):
        uuid += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
    return uuid


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


def get_channel_id():
    with open("config.json", "r") as f:
        config = json.load(f)
        diskord_channel_id = config["diskord_channel_id"]
    return diskord_channel_id


def save_to_config(thread_id, thread_url, thread_name):
    config_name = "temp/ids_config.json"
    # create temp directory if it doesn't exist
    directory = os.path.dirname(config_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # create config if it doesn't exist
    try:
        with open(config_name, "r") as f:
            pass
    except FileNotFoundError:
        with open(config_name, "w") as f:
            json.dump([], f, indent=4)

    # save to config
    with open(config_name, "r") as f:
        ids_config = json.load(f)
        ids_config.append({"thread_id": thread_id, "thread_name": thread_name, "thread_url": thread_url})
    with open(config_name, "w") as f:
        json.dump(ids_config, f, indent=4)


# json cleanup
def json_cleanup(json_data):
    cleaned_data = []  # To store the cleaned JSON data
    encountered_names = set()  # To keep track of encountered "file_name" values

    for item in json_data:
        file_name = item.get("file_name")

        if file_name not in encountered_names:
            # If it's a new "file_name," add the item to the cleaned data list
            cleaned_data.append(item)
            # Add the "file_name" to the set of encountered values
            encountered_names.add(file_name)

    return cleaned_data


def save_upload_data(upload_list, thread_id, thread_name, thread_url):
    json_path = f"temp/configs/{thread_name}.json"
    temp_json_path = f"temp/configs/temp/{thread_name}.json"
    thread_json_path = "temp/ids_config.json"
    try:
        with open(json_path, "r") as f:
            pass
    except FileNotFoundError:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(json_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            # create a temps subdirectory in the directory
            os.makedirs(f"{directory}/temp")

        # Create the JSON file and write an empty array to ithttps://discord.com/channels/1141002753754288160/1151661938791677983
        with open(json_path, "w") as f:
            json.dump([], f, indent=4)

    with open(json_path, "r") as f:
        ids_config = json.load(f)
        ids_config.append({"thread_id": thread_id, "thread_name": thread_name,
                           "thread_url": thread_url})

    # combine json files
    # remove json from upload_list
    upload_list = [i for i in upload_list if i["file_name"] != f"{thread_name}.json"]

    # add upload_list to "files" key in data_json.json
    # create db_dir if it doesn't exist
    db_dir_path = "db_dir"
    if not os.path.exists(db_dir_path):
        os.makedirs(db_dir_path)

    json_path = f"db_dir/{thread_name}.json"
    with open(temp_json_path, "r") as f:
        data_json = json.load(f)
        data_json["files"] = upload_list

        # add thread info
        with open(thread_json_path, "r") as f:
            thread_json = json.load(f)
            for i in thread_json:
                if i["thread_name"] == thread_name:
                    # remove thread_name key
                    del i["thread_name"]
                    data_json["thread_info"] = i

    with open(json_path, "w") as f:
        json.dump(data_json, f, indent=4)

    write_to_db(data_json)

    # delete the temp json files
    temp_file_1 = f"temp/configs/temp/{thread_name}.json"
    temp_file_2 = f"temp/configs/{thread_name}.json"

    os.remove(temp_file_1)
    os.remove(temp_file_2)
    # print number of files
    print(
        f"{current_time()}{Fore.BLUE} {len(upload_list)} files uploaded in thread" + Fore.YELLOW + f"[{thread_name}]" + Fore.RESET)


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('/', ';'), intents=discord.Intents.all())

        self.cogslist = ["cogs.help", "cogs.setup", "cogs.mod", "cogs.diskord"]

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
            print(f"{current_time()}{Fore.BLUE} CONFIG:{Fore.GREEN} Channel id saved" + Fore.RESET)

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

    # listen for messages
    async def on_message(self, message):
        channel_id = get_channel_id()
        channel = message.channel
        if message.channel.id == channel_id:
            if message.author.id != self.user.id:

                # get message content
                content = message.content

                # Thread creation
                if content.startswith("//thread"):
                    server_owner = message.guild.owner
                    try:
                        thread_name = content.split("//thread ")[1]

                        thread = await channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
                        thread_url = thread.jump_url
                        thread_id = thread.id

                        save_to_config(thread_id, thread_url, thread_name)

                        # await message.add_reaction("✅")
                        # await thread.send(f"{server_owner.mention} New file uploaded")

                        # Attachment urls
                        upload_list = []
                        end_flag = False
                        chunks_number = 0

                        while True:
                            if end_flag:
                                break
                            thread = self.get_channel(thread_id)
                            async for message in thread.history(limit=100):
                                for attachment in message.attachments:
                                    if attachment.url in [i["file_url"] for i in upload_list]:
                                        continue
                                    else:
                                        file_name = attachment.filename
                                        file_url = attachment.url
                                        entry = {"file_name": file_name, "file_url": file_url}

                                        upload_list.append(entry)
                                        # await message.add_reaction("✅")

                                    # download metadata json from attachment named {thread_name}.json and get 'chunks' number
                                    if file_name == f"{thread_name}.json":
                                        # get message id
                                        message_id = message.id

                                        file_path = f"temp/configs/temp/{thread_name}.json"
                                        # check if temp directory exists and create it if it doesn't
                                        directory = os.path.dirname(file_path)
                                        if not os.path.exists(directory):
                                            os.makedirs(directory)

                                        await attachment.save(file_path)

                                        await message.delete()

                                        with open(file_path, "r") as f:
                                            config = json.load(f)
                                            chunks_number = config["chunks_number"]

                                            print("c1", chunks_number)

                                # TODO: fix this (monitor thread until all files are uploaded and then save the json)

                                upload_list = json_cleanup(upload_list)

                                # Save upload data
                                # if len(upload_list) == chunks_number + 1 and not end_flag:
                                #     save_upload_data(upload_list, thread_id, thread_name, thread_url)
                                #     embed = discord.Embed(title="Upload saved", color=discord.Color.green())
                                #     # send embed to thread and lock thread to read only
                                #     await thread.send(embed=embed)
                                #     await thread.edit(archived=True)
                                #
                                #     end_flag = True
                                #     break

                                # failsafe [listen for //end message]
                                if message.content == "//end":
                                    # get the message id for the //end message
                                    end_message_id = message.id

                                    # check if all files are uploaded
                                    if len(upload_list) == chunks_number + 1 and not end_flag:
                                        save_upload_data(upload_list, thread_id, thread_name, thread_url)
                                        embed = discord.Embed(title="Upload saved", color=discord.Color.green())
                                        # send embed to thread and lock thread to read only
                                        await thread.delete_messages([discord.Object(id=end_message_id)])
                                        await thread.send(embed=embed)
                                        await thread.edit(archived=True)

                                        end_flag = True

                                        break

                    except Exception as e:
                        # await message.add_reaction("❌")
                        # await message.delete(delay=5)
                        print(e)


                # Embed
                elif message.embeds:
                    pass
                elif message.attachments:
                    pass
                else:
                    await message.add_reaction("🚫")
                    await message.delete(delay=5)

                # TODO: add file upload detection


client = Client()
client.run(token)
