import datetime
import json

import discord
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


class mod(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # clearall
    @app_commands.command(name="clearall", description="Clear all messages in a channel")
    async def clearall(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # delete all messages in the channel and get the number of deleted messages
        deleted = await interaction.channel.purge(limit=None)

        embed = discord.Embed(title="Channel Purged", description=f"Cleared ({len(deleted)}) messages",
                              color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())
        message = await interaction.followup.send(embed=embed)
        await message.delete(delay=5)


        print(
            f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/clearall {Fore.RESET}")

    # reset
    @app_commands.command(name="reset", description="Reset the server")
    async def reset(self, interaction: discord.Interaction):
        try:
            sender = interaction.user
            # delete all categories, channels and roles then create a new general channel
            guild = interaction.guild

            # delete all categories
            for category in guild.categories:
                await category.delete()

            # delete all channels
            for channel in guild.channels:
                await channel.delete()

            # create a new general channel
            await guild.create_text_channel("general")
            # update config
            with open("config.json", "r") as f:
                config = json.load(f)
                config["diskord_channel_id"] = ""
                config["webhook_url"] = ""
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)

            embed = discord.Embed(title="Server Reset",
                                  description=f"Server has been reset by {interaction.user.mention}",
                                  color=discord.Color.purple(), timestamp=datetime.datetime.utcnow())

            embed.set_thumbnail(url=self.client.user.avatar)
            await guild.text_channels[0].send(embed=embed, delete_after=5)

            print(
                f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/reset {Fore.RESET}")
        # show errors
        except Exception as e:
            print(e)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(mod(client))
