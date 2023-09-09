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

class help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="help", description="get a list of all commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = await interaction.followup.send(f"sending help...")
        embed = discord.Embed(title="Help", color=discord.Color.red(),timestamp=datetime.datetime.utcnow())
        bot_avatar = self.client.user.avatar
        embed.set_thumbnail(url=bot_avatar)
        embed.url = "https://ups.maev.site"

        embed.add_field(name="__NSFW Commands__", value=f"`/nsfwcheck`: Check if an image is NSFW. \n`/nsfwsearch`: Search for NSFW videos across multiple sites. \n`/nsfwvideo [number]`: Request a number of videos. \n`/nsfwvideo cached`: Get a random cached video. \n `/nsfwvideo stats`: Show server stats. \n`/nsfwvideo help`: Show the nsfwvideo help page.", inline=False)
        embed.add_field(name="__Help Commands__", value="`/help`: Show this tab", inline=False)
        if interaction.guild is not None:
            try:
                embed.set_thumbnail(url=interaction.guild.icon)
            except discord.HTTPException:
                print("Guild icon not found, skipping thumbnail")

        await message.edit(content=None, embed=embed)
        print(f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/help {Fore.RESET}")





async def setup(client: commands.Bot) -> None:
    await client.add_cog(help(client))