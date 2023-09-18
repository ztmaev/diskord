import datetime
import math
import discord
import mysql.connector
from colorama import Fore, Style
from discord import app_commands
from discord.ext import commands


# time in gmt+3
def current_time():
    current_time = datetime.datetime.utcnow()
    # return current time
    return current_time


def get_db():
    db = mysql.connector.connect(
        host="arc.maev.site",
        user="maev",
        passwd="Alph4",
        port="3306",
        database="test"
    )
    return db


def convert_file_size_to_kb(file_size):
    file_size = file_size.strip().lower()

    if "kb" in file_size:
        return int(float(file_size.replace("kb", "").strip()))
    elif "mb" in file_size:
        return int(float(file_size.replace("mb", "").strip()) * 1000)
    elif "gb" in file_size:
        return int(float(file_size.replace("gb", "").strip()) * 1000000)
    else:
        raise ValueError("Invalid file size format. Please use 'KB', 'MB', or 'GB'.")


def convert_file_size(size_kb):
    if size_kb == 0:
        return "0KB"
    size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0  # Size is already in KB
    while size_kb >= 1024 and i < len(size_name) - 1:
        size_kb /= 1024.0
        i += 1
    s = round(size_kb, 2)
    return f"{s} {size_name[i]}"


def parse_file_sizes(files):
    total_size = 0
    for file in files:
        file_size_str = file[2]  # Assuming the file size is always at index 2 in each 'file' tuple
        file_size = float(file_size_str.split()[0])  # Extract the numeric part and convert to float
        unit = file_size_str.split()[1]  # Extract the unit (e.g., 'KB', 'MB', etc.)

        if unit == 'KB':
            total_size += file_size  # Add the size in kilobytes directly
        elif unit == 'MB':
            total_size += file_size * 1024  # Convert megabytes to kilobytes and add
        elif unit == 'GB':
            total_size += file_size * 1024 * 1024  # Convert gigabytes to kilobytes and add

    return total_size


def fetch_user_data(user_id):
    db = get_db()
    # check files table
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM files WHERE owner_id = {user_id}")
    result = cursor.fetchall()
    if len(result) == 0:
        return {"files_no": 0, "total_size": 0, "total_downloads": 0}
    else:
        files_no = len(result)
        # get total_size
        total_size = parse_file_sizes(result)

    # return data
    return {"files_no": files_no, "total_size": total_size, "total_downloads": 0}


class diskord(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="files", description="get details about files hosted on diskord")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = await interaction.followup.send(f"fetching info...")
        user_id = interaction.user.id
        user_data = fetch_user_data(user_id)

        embed = discord.Embed(title=f"File info", color=discord.Color.purple(), timestamp=current_time())

        bot_avatar = self.client.user.avatar
        embed.set_thumbnail(url=bot_avatar)
        embed.url = "https://diskord.maev.site"
        user_id = interaction.user.id
        user_data = fetch_user_data(user_id)
        no_of_files = user_data["files_no"]
        total_size = user_data["total_size"]
        total_size = convert_file_size(total_size)
        embed.add_field(name=f"File info for {interaction.user}",
                        value=f"**Files hosted:** {no_of_files}\n**Total size:** {total_size}\n", inline=False)

        if interaction.guild is not None:
            try:
                embed.set_thumbnail(url=interaction.guild.icon)
            except discord.HTTPException:
                print("Guild icon not found, skipping thumbnail")

        await message.edit(content=None, embed=embed)
        print(
            f"{current_time()}{Fore.CYAN} {interaction.user}{Fore.RESET + Fore.WHITE + Style.BRIGHT} used command {Fore.YELLOW}/files {Fore.RESET}")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(diskord(client))
