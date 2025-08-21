# main.py
import discord
from discord.ext import commands
import os


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logado com sucesso como {bot.user}!')
    print('Carregando Cogs...')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Cog {filename} carregado com sucesso.')
            except Exception as e:
                print(f'Falha ao carregar o Cog {filename}: {e}')
    print('------------------------------------')
    print('Robô está online e pronto para uso!')


@bot.command()
@commands.is_owner()
async def sync(ctx, spec: str = None):
    if spec == "clear":
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Comandos locais limpos para este servidor.")
        return
    guild = ctx.guild
    ctx.bot.tree.copy_global_to(guild=guild)
    synced = await ctx.bot.tree.sync(guild=guild)
    await ctx.send(f"Sincronizado {len(synced)} comandos para este servidor.")


token = os.environ['DISCORD_TOKEN']
bot.run(token)
