import datetime

import discord
import json
from colorama import Fore, Style, Back
from discord import app_commands
from discord.ext import commands


# time in gmt+3
def current_time():
    utc_time = datetime.datetime.utcnow()
    gmt3_time = utc_time + datetime.timedelta(hours=3)
    gmt3_time_full = (Back.BLACK + Fore.GREEN + gmt3_time.strftime(
        "%d/%m/%y %H:%M:%S") + Back.RESET + Fore.WHITE + Style.BRIGHT)
    return gmt3_time_full

def save_to_config(diskord_channel_id, webhook_url):
    # webhook url
    with open("config.json", "r") as f:
        config = json.load(f)
        config["webhook_url"] = webhook_url
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    # channel id
    with open("config.json", "r") as f:
        config = json.load(f)
        config["diskord_channel_id"] = diskord_channel_id
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)



class setups(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # setuptest
    @app_commands.command(name="cogsetup", description="test if cog `help`is working")
    async def cogsetup(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Working", description="Cog `setup` is working", color=discord.Color.purple(),
                              timestamp=datetime.datetime.utcnow())
        await interaction.response.send_message(embed=embed)
        print(
            f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/cogsetup {Fore.RESET}")

    # setup command
    @app_commands.command(name="newsetup", description="Setup server for file storage")
    async def newsetup(self, interaction: discord.Interaction):
        category_name = "Automated"
        channel_name = "diskord"

        await interaction.response.defer(ephemeral=True)

        # start
        embed = discord.Embed(title="Server setup", color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Server setup starting... ", value=f"""
                        ❌ Create category `{category_name}`.
                        ❌ Create channel `{channel_name}`.
        
        """, inline=False)

        await interaction.followup.send(embed=embed)


        if discord.utils.get(interaction.guild.categories, name=category_name) is None:
            guild = interaction.guild
            category = await guild.create_category(category_name)
            embed = discord.Embed(title="⚙️ Server setup", color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Server setup started... ", value=f"""
                        ✅ Create category `{category_name}`.
                        ❌ Create channel `{channel_name}`.
                        """, inline=False)
            embed.set_thumbnail(url=self.client.user.avatar)
            await interaction.edit_original_response(embed=embed)
            
        else:
            category = discord.utils.get(interaction.guild.categories, name=category_name)
            embed = discord.Embed(title="⚙️ Server setup", color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Server setup started... ", value=f"""
                        ✅ Create category `{category_name}`.
                        ❌ Create channel `{channel_name}`.
                        """, inline=False)
            embed.set_thumbnail(url=self.client.user.avatar)
            await interaction.edit_original_response(embed=embed)

        if discord.utils.get(interaction.guild.channels, name=channel_name) is None:
            await guild.create_text_channel(channel_name, category=category)

            #create webhook and get it's url
            channel = discord.utils.get(interaction.guild.channels, name=channel_name)
            webhook = await channel.create_webhook(name="Maevey")
            webhook_url = webhook.url

            diskord_channel_id = channel.id

            save_to_config(diskord_channel_id, webhook_url)

            embed = discord.Embed(title="⚙️ Server setup", color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Server setup complete. ", value=f"""
                        ✅ Create category `{category_name}`.
                        ✅ Create channel `{channel_name}`.
                        """, inline=False)
            embed.set_thumbnail(url=self.client.user.avatar)
            await interaction.edit_original_response(embed=embed)

        else:
            embed = discord.Embed(title="⚙️ Server setup", color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Server setup complete. ", value=f"""
                        ✅ Create category `{category_name}`.
                        ✅ Create channel `{channel_name}`.
                        """, inline=False)
            embed.set_thumbnail(url=self.client.user.avatar)
            await interaction.edit_original_response(embed=embed)

        print(
            f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/newsetup {Fore.RESET}")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(setups(client))
