import discord
import asyncio
import json
import datetime
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        with open("required files/channels.json", "r") as f:
            data=json.load(f)
        try:
            logChannel=self.bot.get_channel(int(data[str(message.guild.id)]['log']))
            embed=discord.Embed(title=f"Message deleted in {message.channel}", color=65280)
            embed.add_field(name=f"{message.author}", value=message.content)
            embed.timestamp=datetime.datetime.utcnow()
            await logChannel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        with open("required files/channels.json", "r") as f:
            data=json.load(f)
        try:
            logChannel=self.bot.get_channel(int(data[str(after.guild.id)]['log']))
            embed=discord.Embed(title=f"Message edited by {after.author} in {after.channel}", color=65280)
            before_content=None
            after_content=None
            if before.content is None:
                before_content="*Embed or image*"
            else:
                before_content=before.content
            if after.content is None:
                after_content="*Embed or image"
            else:
                after_content=after.content
            if before_content==after_content:
                return
            embed.add_field(name="Original message", value=before_content, inline=False)
            embed.add_field(name="New message", value=after_content, inline=False)
            embed.timestamp=datetime.datetime.utcnow()
            await logChannel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        with open("required files/channels.json", "r") as f:
            data=json.load(f)
        try:
            logChannel=self.bot.get_channel(int(data[str(guild.id)]['log']))
            embed=discord.Embed(title=f"User has been banned from the server", color=65280)
            embed.add_field(name=f"User", value=str(member))
            embed.timestamp=datetime.datetime.utcnow()
            await logChannel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("required files/channels.json", "r") as f:
            data=json.load(f)
        try:
            logChannel=self.bot.get_channel(int(data[str(member.guild.id)]['log']))
            embed=discord.Embed(title="A member has joined the guild",  description=f"{str(member)} - {member.id}\nAccount created at {member.created_at.strftime('%d %b %Y %H:%M')}", color=65280)
            embed.timestamp=datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar_url)
            await logChannel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open("required files/channels.json", "r") as f:
            data=json.load(f)
        try:
            logChannel=self.bot.get_channel(int(data[str(member.guild.id)]['log']))
            embed=discord.Embed(title="A member is no longer in the guild",  description=f"{str(member)} - {member.id}", color=65280)
            embed.timestamp=datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar_url)
            await logChannel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_takagi_mod_action(self, action, user, moderator, reason):
        with open("required files/channels.json", "r") as f:
            data=json.load(f)
        try:
            logChannel=self.bot.get_channel(int(data[str(user.guild.id)]['log']))
            embed=discord.Embed(title=f"User has been {action}", description=f"{user} - {user.id}", color=65280)
            embed.add_field(name=f"Moderator", value=moderator)
            embed.add_field(name="Reason", value=reason)
            embed.set_thumbnail(url=user.avatar_url_as(static_format="png"))
            embed.timestamp=datetime.datetime.utcnow()
            await logChannel.send(embed=embed)
        except:
            pass



def setup(bot):
    bot.add_cog(Logging(bot))
