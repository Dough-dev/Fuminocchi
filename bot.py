import discord
from discord.ext import commands, tasks

client = commands.Bot(command_prefix = '+')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('with Yuiga-kun. +help'))
    print('Bot is ready.')

@client.event
async def on_member_join(member):
    print(f'Welcome {member} to the r/Furuhshi Discord!')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('The specified command does not exist.')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limt=amount)
    await ctx.send(f'{amount} messages cleared.')

@clear.error
async def clear(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the number of messages you would like to clear.')

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')

@kick.error
async def kick(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the user you would like to kick.')

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention} Shoo shoo, away from the glory of Foom!')

@ban.error
async def ban(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the user you would like to ban.')

@client.command()
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

#cogs, broken atm
#@client.command()
#async def load(ctx, extension):
#    client.load_extension(f'cogs.{extension}')

#@client.command()
#async def unload(ctx, extension):
#    client.unload_extension(f'cogs.{extension}')

#for filename in os.listdir('./cogs'):
#    if filename.endswith('.py'):
#        client.load_extension(f'cogs.{filename[:-3]}')

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    guild = ctx.message.guild
    voice_client = guild.voice_client
    await voice_client.disconnect()

@client.command(pass_context=True)
async def play(ctx, url):
    guild = ctx.message.guild
    voice_client = guild.voice_client
    player = await voice_client.create_ytdl_player(url)
    players[server.id] = player
    player.start

client.run('NTEzMjE5NDI5NTU1ODk2MzIy.XgUrDg.e2iBPMaqGWbzvYMzy-kkqW3qHbA')
