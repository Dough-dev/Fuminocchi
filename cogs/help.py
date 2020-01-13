import discord
import asyncio
import json
from discord.ext import commands
from disputils import BotEmbedPaginator

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.command(name="""help""", aliases=["""commands"""])
    async def help(self, ctx, request=None):
        if not request:
            embeds=[
                discord.Embed(title='''Utility''', description="""**help** - Shows this help message.
**info** - Gives you info about Fuminocchi
**serverinfo** - Gives you info about the server
**userinfo [@member]** - Gives you info about your (or someone else's) Discord account
**avatar [@member]** - Sends yours or someone else's avatar in the chat""", color=63458),
                discord.Embed(title='''Other''', description='''**poll <"question"> options** - Creates a poll for others to vote on.''', color=63458),
                discord.Embed(title='''Moderation''', description='''**kick <@member> [reason]** - Kicks a member from the server
**ban <@member> [reason]** - Bans a member from the server.
**mute <@member> [reason]** - Mutes a member
**unmute <@member> [reason]** - Unmutes a member
**clear <number>** - Deletes a number of messages''', color=63458),
                discord.Embed(title='''Roles''', description='''**join <role name>** - Joins a role
**leave <role name>** - Leaves a role
**roles** - Shows you a list of assignable roles
**autorole [add/remove <role name>]** - Shows you this guild's roles, or add/removes them.''', color=63458),
            ]
            paginator=BotEmbedPaginator(ctx, embeds)
            await paginator.run()
        elif request.lower()=="""help""":
            embed=discord.Embed(title="""Help""", description="""This command shows you all commands or help for a particular command.""", color=63458)
            embed.add_field(name="""Aliases""", value="""help
commands""", inline=False)
            embed.add_field(name="""Usage""", value="""`help [optional command]`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""info""":
            embed=discord.Embed(title="""Info""", description="""This command shows you information about Fuminocchi.""", color=63458)
            embed.add_field(name="""Aliases""", value="""info""", inline=False)
            embed.add_field(name="""Usage""", value="""`info`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""serverinfo""":
            embed=discord.Embed(title="""Serverinfo""", description="""Gives information about the server.""", color=63458)
            embed.add_field(name="""Aliases""", value="""serverinfo
guildinfo
server
guild""", inline=False)
            embed.add_field(name="""Usage""", value="""`serverinfo`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""userinfo""":
            embed=discord.Embed(title="""Userinfo""", description="""Gives you information about you or another user.""", color=63458)
            embed.add_field(name="""Aliases""", value="""userinfo
user""", inline=False)
            embed.add_field(name="""Usage""", value="""`userinfo [optional name/mention]`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""avatar""":
            embed=discord.Embed(title="""Help""", description="""Sends your or someone else's avatar in the chat.""", color=63458)
            embed.add_field(name="""Aliases""", value="""avatar
profilephoto
photo""", inline=False)
            embed.add_field(name="""Usage""", value="""`avatar [optional user]`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""poll""":
            embed=discord.Embed(title="""Help""", description="""Creates a poll and allows users to vote on it.""", color=63458)
            embed.add_field(name="""Aliases""", value="""poll""", inline=False)
            embed.add_field(name="""Usage""", value="""`poll <'Question in quotes'> <'options' 'separated' 'by' 'a' 'space' 'in' 'quotes'>`
You can add up to 10 options""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""giveaway""":
            embed=discord.Embed(title="""Giveaway""", description="""Draws giveaway winner after x time.""", color=63458)
            embed.add_field(name="""Aliases""", value="""giveaway""", inline=False)
            embed.add_field(name="""Usage""", value="""`giveaway <required duration in days> <required prize>`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Administrator""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""kick""":
            embed=discord.Embed(title="""Kick""", description="""Kicks member from the server.""", color=63458)
            embed.add_field(name="""Aliases""", value="""kick""", inline=False)
            embed.add_field(name="""Usage""", value="""`kick <required @member> [optional reason]`
The reason is not required but will show in the audit log and logging channel (if set)""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Kick members""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""ban""":
            embed=discord.Embed(title="""Ban""", description="""Bans a member from the server.""", color=63458)
            embed.add_field(name="""Aliases""", value="""ban""", inline=False)
            embed.add_field(name="""Usage""", value="""`ban <required @member> [optional reason]
The reason is not required but will show in the audit log and logging channel (if set)`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Ban members""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""mute""":
            embed=discord.Embed(title="""Mute""", description="""Unmutes a member.""", color=63458)
            embed.add_field(name="""Aliases""", value="""mute""", inline=False)
            embed.add_field(name="""Usage""", value="""`mute <@member> [optional reason]`
The reason is not required but will show in the audit log and logging channel (if set)""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Kick members""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""unmute""":
            embed=discord.Embed(title="""Unmute""", description="""Unmutes a member.""", color=63458)
            embed.add_field(name="""Aliases""", value="""unmute""", inline=False)
            embed.add_field(name="""Usage""", value="""`unmute <required @member> <optional reason>`
The reason is not required but will show in the audit log and logging channel (if set)""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Kick members""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""clear""":
            embed=discord.Embed(title="""Clear""", description="""Clears the specified number of messages.""", color=63458)
            embed.add_field(name="""Aliases""", value="""clear
purge""", inline=False)
            embed.add_field(name="""Usage""", value="""`clear <required number>`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Manage messages""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""join""":
            embed=discord.Embed(title="""Join""", description="""Allows you to add a role.""", color=63458)
            embed.add_field(name="""Aliases""", value="""join
role
joinrole""", inline=False)
            embed.add_field(name="""Usage""", value="""`join <required role name>`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""leave""":
            embed=discord.Embed(title="""Leave""", description="""Allows you to remove a role.""", color=63458)
            embed.add_field(name="""Aliases""", value="""leave
leaverole""", inline=False)
            embed.add_field(name="""Usage""", value="""`leave <required role name>`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""roles""":
            embed=discord.Embed(title="""Roles""", description="""Shows you all the roles you can add.""", color=63458)
            embed.add_field(name="""Aliases""", value="""roles
ranks""", inline=False)
            embed.add_field(name="""Usage""", value="""`roles`""", inline=False)
            embed.add_field(name="""Required permissions""", value="""None""", inline=False)
            await ctx.send(embed=embed)
        elif request.lower()=="""autorole""":
            embed=discord.Embed(title="""Autorole""", description="""Shows you this guild's autoroles, and allows you to add and remove them.""", color=63458)
            embed.add_field(name="""Aliases""", value="""autorole
ar""", inline=False)
            embed.add_field(name="""Usage""", value="""`autorole [add/remove <role name>]`
If you don't say add or remove, it will show you the guild's autoroles. If you say add/remove, you must specify a role name""", inline=False)
            embed.add_field(name="""Required permissions""", value="""Manage roles""", inline=False)
            await ctx.send(embed=embed)

        else:
            return await ctx.send("""That isn't a valid command. Use **help** to see whats available""")



def setup(bot):
    bot.add_cog(Help(bot))
