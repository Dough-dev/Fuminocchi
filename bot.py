import discord
from discord.ext import commands, tasks
import asyncio
import json
import datetime
import lavalink

bot = commands.Bot(command_prefix = '+')
bot.remove_command('help')
bot.bootTime=datetime.datetime.utcnow()
bot.now = datetime.datetime.utcnow().day
with open("config.json", "r") as ff:
    conf=json.load(ff)

@bot.event
async def on_ready():
    try:
        bot.load_extension('cogs.help')
        print("Loaded help.")
    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to  load extension {extension}\n{exc}')
    try:
        bot.load_extension('cogs.logging')
        print("Loaded logging.")
    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to  load extension {extension}\n{exc}')
    try:
        bot.load_extension('cogs.other')
        print("Loaded other.")
    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to  load extension {extension}\n{exc}')
    try:
        bot.load_extension('cogs.roles')
        print("Loaded roles.")
    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to  load extension {extension}\n{exc}')
    try:
        bot.load_extension('cogs.utility')
        print("Loaded utility.")
    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to  load extension {extension}\n{exc}')
    print('Ready!')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('with Yuiga-kun. - +help'))
    print('Bot is ready.')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='fumihi')
    await channel.send(f"Welcome {member.mention} to the r/Furuhashi discord server! <:fumihi:666073632354598912> Read the rules in <#650449886180802570> and then hop onto <#648954224628989964> to talk with us! <:sipmino:666073632354598912>")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('The specified command does not exist.')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{amount} messages cleared.')

@clear.error
async def clear(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the number of messages you would like to clear.')

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')

@kick.error
async def kick(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the user you would like to kick.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention} Shoo shoo, away from the glory of Foom!')

@ban.error
async def ban(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the user you would like to ban.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
            return

@unban.error
async def unban(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the user you would like to unban.')

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def mute(ctx, member: discord.Member):
    if not member:
      await ctx.send("Who do you want me to mute?")
      return
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(role)
    await ctx.send("Member has been muted!")

@mute.error
async def mute_error(ctx, error):
  if isinstance(error, commands.CheckFailure):
    await ctx.send("You are not allowed to mute!")

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def unmute(ctx, member:discord.User=None, reason=None):
  if not member:
    await ctx.send("Who needs to be unmuted?")
    return
  role = discord.utils.get(ctx.guild.roles, name="Muted")
  await member.remove_roles(role)
  await ctx.send("Member has been unmuted!")

@unmute.error
async def unmute_error(ctx, error):
  if isinstance(error, commands.CheckFailure):
    await ctx.send("You are not allowed to unmute!")

#--------------------------------------------------------------------------------------------------------------------------------

@bot.command(name="load")
async def load(ctx, cog=None):
    if await ctx.bot.is_owner(ctx.author):
        if not cog:
            await ctx.send("You didn't say which cog to load")
        else:
            try:
                bot.load_extension("cogs."+str(cog))
                await ctx.send("`{}` has been loaded".format(cog))
            except Exception as E:
                await ctx.send(f"There was a problem loading `{cog}`, ```{E}```")
    else:
        await ctx.send("Only the bot owner can manage extensions.")

@bot.command(name="unload")
async def unload(ctx, cog=None):
    if await ctx.bot.is_owner(ctx.author):
        if not cog:
            await ctx.send("You didn't say which cog to load")
        else:
            try:
                bot.unload_extension("cogs."+str(cog))
                await ctx.send("`{}` has been unloaded".format(cog))
            except Exception as E:
                await ctx.send(f"There was a problem unloading `{cog}`, ```{E}```")
    else:
        await ctx.send("You don't have permission to manage extensions.")

@bot.command(name="reload")
async def reload(ctx, cog=None):
    if await ctx.bot.is_owner(ctx.author):
        if not cog:
            await ctx.send("You didn't say which cog to load")
        else:
            try:
                bot.unload_extension("cogs."+str(cog))
                bot.load_extension("cogs."+str(cog))
                await ctx.send("`{}` has been reloaded".format(cog))
            except Exception as E:
                await ctx.send(f"There was a problem reloading `{cog}`, ```{E}```")
    else:
        await ctx.send("You don't have permission to manage extensions.")

#--------------------------------------------------------------------------------------------------------------------------------

#Fumino Reaction Commands

@bot.command()
async def fumiblush(ctx):
    await ctx.send(f'https://cdn.discordapp.com/attachments/460635108815142922/660694868338802708/fumisick.png')

#--------------------------------------------------------------------------------------------------------------------------------

bot.run('token', reconnect=True)
