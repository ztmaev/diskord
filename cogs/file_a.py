import discord
import datetime
from colorama import Fore, Style, Back
from discord.ext import commands
from discord import app_commands

#time in gmt+3
def current_time():
    utc_time = datetime.datetime.utcnow()
    gmt3_time = utc_time + datetime.timedelta(hours=3)
    gmt3_time_full = (Back.BLACK + Fore.GREEN + gmt3_time.strftime(
        "%d/%m/%y %H:%M:%S") + Back.RESET + Fore.WHITE + Style.BRIGHT)
    return gmt3_time_full

class file_a(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    #setuptest
    @app_commands.command(name="cogfile_a", description="test if cog `file_a`is working")
    async def cogfile_a(self, interaction: discord.Interaction):
       embed = discord.Embed(title="Working", description="Cog `file_a` is working", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())
       await interaction.response.send_message(embed=embed)
       print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/cogfile_a {Fore.RESET}")

    # setup command
    @app_commands.command(name="clearall", description="Clear all messages in a channel")
    async def clearall(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # delete all messages in the channel and get the number of deleted messages
        deleted = await interaction.channel.purge(limit=None)

        embed = discord.Embed(title="Channel Purged", description=f"Cleared ({len(deleted)}) messages", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())
        await interaction.followup.send(embed=embed)

        print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/clearall {Fore.RESET}")



async def setup(client: commands.Bot) -> None:
    await client.add_cog(file_a(client))