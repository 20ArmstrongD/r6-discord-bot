import discord
from discord import app_commands
import logging
import time
import inspect
from events import (
    checkEnvVar, 
    DISCORD_BOT_TOKEN,
    GUILD_ID,
    botstuff,
    intent,
    on_Ready,
    get_r6siege_player_data,
    generate_link, 
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p'  # 12-hour clock with AM/PM
)

# Confirm .env variables are correct and loading properly
checkEnvVar()

# Init bot intents
intents = intent
intents.message_content = True

bot = botstuff

# Bot event for on_ready
@bot.event
async def on_ready():
    await on_Ready()


game_choices = [
    app_commands.Choice(name = "Fortnite", value = "fortnite"),
    app_commands.Choice(name = "Rainbow Six Siege", value = "siege"),
    ]
# Slash command definition
@bot.tree.command(guild=discord.Object(id=GUILD_ID), name="game_stats", description="Fetch game stats for a player")
@app_commands.describe(username="Enter the player's name",game='Choose a game' ,platform="Enter the platform (PC, Xbox, PlayStation)")
@app_commands.choices(game=game_choices)
async def pull_stats(interaction: discord.Interaction, game: app_commands.Choice[str], username: str, platform: str = None, ):

    game = game.value
    print(f"Selected game: {game}")
    user = interaction.user
    channel_location = interaction.channel
    await interaction.response.defer()
    start_time = time.time()
    if platform is not None:
        platform = platform.lower()
        try:
            
            if platform == 'pc':
                logging.info(f"{platform} element found")
                platform = 'ubi'
            elif platform == 'xbox':
                logging.info(f"{platform} element found")
                platform = 'xbl'
            elif platform == 'playstation':
                logging.info(f"{platform} element found")
                platform = 'psn'
            else:
                logging.error(f"Failed to find {platform} platform")
                await interaction.followup.send("Failed to find platform. Please try again later.")
                return  # Exit early if the platform is invalid
        except Exception as e:
            print("failed to convert platform")   
    else:
        pass 

    game_scrapers = {
        "siege": {"func": get_r6siege_player_data, "requires_platform": True},
        "fortnite": {"func": get_fortnite_player_data, "requires_platform": False}
    }

    print(f"Received game: '{game}', Lowercased: '{game.lower()}'")

    if game not in game_scrapers:
        await interaction.followup.send(f"{game} not supported. Please pick from these options:")  
        return  

    scraper_functions = game_scrapers[game]["func"]
    requires_platform = game_scrapers[game]["requires_platform"]
    
    if requires_platform and not platform:
        await interaction.followup.send(f"{game} requires a platform (PC, Xbox, PSN)")
    
    num_args = len(inspect.signature(scraper_functions).parameters)
    # if asyncio.iscoroutinefunction(scraper_functions):
    if num_args == 2:
        kd, level, playtime, rank, ranked_kd, user_profile_img, rank_img = await get_r6siege_player_data(username, platform)

        # If any value is None, provide a default
        kd = kd if kd is not None else "N/A"
        level = level if level is not None else "N/A"
        playtime = playtime if playtime is not None else "N/A"
        rank = rank if rank is not None else "N/A"
        ranked_kd = ranked_kd if ranked_kd is not None else "N/A"
        user_profile_img = user_profile_img if user_profile_img is not None else "N/A"
        rank_img = rank_img if rank_img is not None else "N/A"
        

        # Use the values as needed
        print(f"KD: {kd}, Level: {level}, Playtime: {playtime}, Rank: {rank}")
        
        embed = discord.Embed(title=f"Stats for {username} on {game.capitalize()}\n", color=discord.Color.yellow())
        embed.add_field(name="**Overall Stats**", value=f" * Level: {level}\n * All playlist KD Ratio: {kd}\n * Total Play Time: {playtime}", inline=False)
        embed.add_field(name="**Ranked Stats**", value=f" * Current Rank: {rank}\n * Ranked KD: {ranked_kd}", inline=False)
        embed.set_thumbnail(url=user_profile_img)  
        embed.set_image(url=rank_img)  
        await interaction.followup.send(embed=embed)

    elif num_args ==1:
        
        url= await generate_link(username)
        
        if url is None:
            await interaction.followup.send("Failed to generate the link.")
            return
        
        embed = discord.Embed(title=f"Here is the link for {username}'s Fortnite stats", color=discord.Color.purple())
        embed.add_field(name="Link", value = f"{url}", inline=False)
        await interaction.followup.send(embed=embed)
    
    else:
        await interaction.followup.send(f"Could not fetch stats for {username} in {game.capitalize()}.**")
        

   

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
