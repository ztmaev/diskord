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

class tests(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    #cogtest
    @app_commands.command(name="cogtest", description="test if cog `help`is working")
    async def cogtest(self, interaction: discord.Interaction):
       embed = discord.Embed(title="Working", description="Cog `tests` is working", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())
       await interaction.response.send_message(embed=embed)
       print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/cogtest {Fore.RESET}")

    #help command to get a list of all commands incliding their description
    @app_commands.command(name="newchannel", description="Create a channel")
    async def newchannel(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="Channel creation", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())

        guild = interaction.guild

        # check if channel already exists in the category 'automated'
        channel = discord.utils.get(guild.channels, name=name)

        if channel is not None:
            embed.add_field(name="Channel", value=f"Channel `{name}` already exists", inline=False)
            await interaction.followup.send(embed=embed)
            return

        # create channel in category auto
        category = discord.utils.get(guild.categories, name="automated")

        if category is None:
            category = await guild.create_category("automated")
            embed.add_field(name="Category", value="Created category `automated`", inline=False)

        await guild.create_text_channel(name, category=category)
        embed.add_field(name="Channel", value=f"Created channel `{name}` in category `{category.name}`", inline=False)

        await interaction.followup.send(embed=embed)
        print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/channel {Fore.RESET}")


    @app_commands.command(name="delchannel", description="Deletes a channel")
    async def delchannel(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="Channel deletion", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())

        guild = interaction.guild

        # check if channel already exists in the category 'automated'
        channel = discord.utils.get(guild.channels, name=name)

        if channel is None:
            embed.add_field(name="Channel", value=f"Channel `{name}` does not exist", inline=False)
            await interaction.followup.send(embed=embed)
            return

        await channel.delete()
        embed.add_field(name="Channel", value=f"Deleted channel `{name}`", inline=False)

        await interaction.followup.send(embed=embed)
        print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/delchannel {Fore.RESET}")

    @app_commands.command(name="newthread", description="Create a thread")
    async def newthread(self, interaction: discord.Interaction, name: str):
        # create a thread in the current channel
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="Thread creation", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())

        channel = interaction.channel
        try:
            thread = await channel.create_thread(name=name)
            if thread:
                await thread.send(f"Hi {interaction.user.mention}! Here is your thread.")
        except discord.Forbidden:
            embed.add_field(name="Thread", value=f"Could not create thread `{name}`", inline=False)
            await interaction.followup.send(embed=embed)
            return

        embed.add_field(name="Thread", value=f"Created thread `{name}`", inline=False)

        await interaction.followup.send(embed=embed)
        print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/newthread {Fore.RESET}")

    @app_commands.command(name="delthread", description="Deletes a thread")
    async def delthread(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="Thread deletion", color=discord.Color.purple(),timestamp=datetime.datetime.utcnow())

        channel = interaction.channel
        try:
            thread = discord.utils.get(channel.threads, name=name)
            if thread:
                await thread.delete()
        except discord.Forbidden:
            embed.add_field(name="Thread", value=f"Could not delete thread `{name}`", inline=False)
            await interaction.followup.send(embed=embed)
            return

        embed.add_field(name="Thread", value=f"Deleted thread `{name}`", inline=False)

        await interaction.followup.send(embed=embed)
        print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/delthread {Fore.RESET}")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(tests(client))