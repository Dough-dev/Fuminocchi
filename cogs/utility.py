import discord
from discord.ext import commands
import asyncio
import datetime
import time
from pathlib import Path
from subprocess import Popen
from platform import python_version
import os
import json

startTime=datetime.datetime.utcnow()

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.command(name='serverinfo', aliases=['guildinfo', 'server', 'guild'])
    async def guildinfo(self, ctx):
        allMembers = set(ctx.guild.members)
        offline = filter((lambda m: (m.status is discord.Status.offline)), allMembers)
        offline = set(offline)
        online = allMembers - offline
        botUsers = filter((lambda m: m.bot), allMembers)
        botUsers = set(botUsers)
        netUsers = allMembers - botUsers
        servericon = ctx.guild.icon_url
        server_passed = (ctx.message.created_at - ctx.guild.created_at).days
        server_created_at = "Created on {}\nThat's {} days ago!".format(ctx.guild.created_at.strftime('%d %b %Y %H:%M'), server_passed)
        embed = discord.Embed(title='Server info', color=63458)
        TextChannelNumber = 0
        VoiceChannelNumber = 0
        Categories = 0
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                TextChannelNumber+=1
            elif isinstance(channel, discord.VoiceChannel):
                VoiceChannelNumber+=1
            else:
                Categories += 1
        boost_status=None
        if not ctx.guild.premium_subscription_count:
            boost_status="There are no members boosting this server"
        else:
            boost_status=f"There are {ctx.guild.premium_subscription_count} members boosting this server"
        embed.add_field(name='Server', value=server_created_at, inline=False)
        embed.add_field(name='Channels', value=((((((str(Categories) + ' Categories\n') + str(TextChannelNumber)) + ' Text channels\n') + str(VoiceChannelNumber)) + ' Voice channels\n') + str(TextChannelNumber + VoiceChannelNumber)) + ' Total channels', inline=False)
        embed.add_field(name='Members', value='{0} total members\n{1} online members\n{2} offline members\n{3} humans\n{4} bots'.format(len(allMembers), len(online), len(offline), len(netUsers), len(botUsers)), inline=False)
        embed.add_field(name='Nitro Boosting', value=f"Boost level {ctx.guild.premium_tier}\n{boost_status}")
        embed.add_field(name='Ownership', value=f'Owned by {ctx.guild.owner}', inline=False)
        embed.set_thumbnail(url=servericon)
        embed.set_footer(text='Server ID: ' + str(ctx.guild.id))
        await ctx.send(embed=embed)

    @guildinfo.error
    async def guildinfo_error(self, ctx, error):
        raise error

    @commands.command(name='userinfo', aliases=["user"])
    async def userinfo(self, ctx, *, userStats=None):
        if (not userStats):
            userStatus = ctx.author.status
            UserIcon = ctx.author.avatar_url
            AccountCreated = ctx.author.created_at.strftime('%d %b %Y %H:%M')
            account_passed = (ctx.message.created_at - ctx.author.created_at).days
            joinedAt = ctx.author.joined_at.strftime('%d %b %Y %H:%M')
            joined_passed = (ctx.message.created_at - ctx.author.joined_at).days
            boost_status=None
            if ctx.author in ctx.guild.premium_subscribers:
                boost_status=f"Has been boosting the server since {ctx.author.premium_since.strftime('%d %b %Y %H:%M')}"
            else:
                boost_status="Not boosting the server"
            embed = discord.Embed(title='User info for {}'.format(ctx.author.name), color=63458)
            embed.add_field(name='Account Info', value="Currently in {} status\nAccount created on {}\nThat's {} days ago!".format(userStatus, AccountCreated, account_passed), inline=False)
            embed.add_field(name='Server Info', value="Joined server on the {}\nThat's {} days ago!\n{}".format(joinedAt, joined_passed, boost_status), inline=False)
            rolesMsg = ''
            for role in ctx.author.roles:
                rolesMsg += str(role) + ', '
            embed.add_field(name='Roles', value=rolesMsg, inline=False)
            embed.set_thumbnail(url=UserIcon)
            embed.set_footer(text='User ID: ' + str(ctx.author.id))
            await ctx.send(embed=embed)
        else:
            if len(userStats)<3:
                await ctx.send("That name is too short. Try mentioning them instead.")
                return
            try:
                found=await self.bot.fetch_user(int(str(userStats)[2:-1]))
                userStatsPing=found.name
                for person in ctx.guild.members:
                    if userStatsPing.lower() in str(person).lower():
                        userStatus = person.status
                        UserIcon = person.avatar_url
                        AccountCreated = person.created_at.strftime('%d %b %Y %H:%M')
                        account_passed = (ctx.message.created_at - person.created_at).days
                        joinedAt = person.joined_at.strftime('%d %b %Y %H:%M')
                        joined_passed = (ctx.message.created_at - person.joined_at).days
                        if person in ctx.guild.premium_subscribers:
                            boost_status=f"Has been boosting the server since {person.premium_since.strftime('%d %b %Y %H:%M')}"
                        else:
                            boost_status="Not boosting the server"
                        embed = discord.Embed(title='User info for {}'.format(person.name), color=63458)
                        embed.add_field(name='Account Info', value="Currently in {} status\nAccount created on {}\nThat's {} days ago!".format(userStatus, AccountCreated, account_passed), inline=False)
                        embed.add_field(name='Server Info', value="Joined server on the {}\nThat's {} days ago!\n{}".format(joinedAt, joined_passed, boost_status), inline=False)
                        rolesMsg = ''
                        for role in person.roles:
                            rolesMsg += str(role) + ', '
                        embed.add_field(name='Roles', value=rolesMsg, inline=False)
                        embed.set_thumbnail(url=UserIcon)
                        embed.set_footer(text='User ID: ' + str(person.id))
                        await ctx.send(embed=embed)
                        return
            except:
                for person in ctx.guild.members:
                    if userStats.lower() in str(person).lower():
                        userStatus = person.status
                        UserIcon = person.avatar_url
                        AccountCreated = person.created_at.strftime('%d %b %Y %H:%M')
                        account_passed = (ctx.message.created_at - person.created_at).days
                        joinedAt = person.joined_at.strftime('%d %b %Y %H:%M')
                        joined_passed = (ctx.message.created_at - person.joined_at).days
                        if person in ctx.guild.premium_subscribers:
                            boost_status=f"Has been boosting the server since {person.premium_since.strftime('%d %b %Y %H:%M')}"
                        else:
                            boost_status="Not boosting the server"
                        embed = discord.Embed(title='User info for {}'.format(person.name), color=63458)
                        embed.add_field(name='Account Info', value="Currently in {} status\nAccount created on {}\nThat's {} days ago!".format(userStatus, AccountCreated, account_passed), inline=False)
                        embed.add_field(name='Server Info', value="Joined server on the {}\nThat's {} days ago!\n{}".format(joinedAt, joined_passed, boost_status), inline=False)
                        rolesMsg = ''
                        for role in person.roles:
                            rolesMsg += str(role) + ', '
                        embed.add_field(name='Roles', value=rolesMsg, inline=False)
                        embed.set_thumbnail(url=UserIcon)
                        embed.set_footer(text='User ID: ' + str(person.id))
                        await ctx.send(embed=embed)
                        return
                await ctx.send("There was a problem getting the info for that user.")

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        await ctx.send('There was a problem getting the info for that user')

    @commands.command(name="me")
    async def me(self, ctx):
        await ctx.invoke(self.bot.get_command("userinfo"))

    @commands.command(name="avatar", aliases=["profilephoto", "photo"])
    async def avatar(self, ctx, user: discord.Member=None):
        embed=discord.Embed(color=63458)
        embed.set_footer(text="Fuminocchi")
        if not user:
            user=ctx.author
        embed.title=f"{user.name}'s avatar"
        embed.description=f"[Link to image]({user.avatar_url_as(static_format='png')})"
        embed.set_image(url=user.avatar_url_as(static_format='png'))
        await ctx.send(embed=embed)

    @avatar.error
    async def avatar_error(self, ctx, error):
        await ctx.send("User not found.")

    @commands.command(name='info')
    async def info(self, ctx):
        startTime=self.bot.bootTime
        timeNow = datetime.datetime.utcnow()
        diff = timeNow - startTime
        (hours, remainder) = divmod(int(diff.total_seconds()), 3600)
        (minutes, seconds) = divmod(remainder, 60)
        (days, hours) = divmod(hours, 24)
        if days:
            timeFormat = '{d} days, {h} hours, {m} minutes and {s} seconds'
        else:
            timeFormat = '{h} hours, {m} minutes and {s} seconds'
        uptimeStamp = timeFormat.format(d=days, h=hours, m=minutes, s=seconds)
        embed = discord.Embed(color=63458)
        embed.add_field(name='Info', value=f'Hello, I am Fuminocchi, the bot for the r/Furuhashi Discord Server! Uptime: {uptimeStamp}\nLatency: {round(self.bot.latency * 1000)}ms', inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
