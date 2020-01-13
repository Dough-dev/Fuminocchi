import discord
from discord.ext import commands
import asyncio
import json
import aiohttp
import random
from PIL import Image, ImageDraw, ImageFont
import os


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.msg=None
        self.emoji_reactions=["{}\U000020E3", "\U0001F51F"]

    @commands.command(name='thank', aliases = ["ty"])
    async def thank(self, ctx, *, userName: discord.Member=None):
        if (not userName):
            await ctx.send(file=discord.File("required files/Thank You Kanye.jpg"))
        else:
            img=Image.open("required files/very cool.png")
            font=ImageFont.truetype("required files/Helvetica.ttf", 35)
            d=ImageDraw.Draw(img)
            text=f"Thank you {userName.name}, very cool!"
            d.text((40, 135), text, font=font, fill=(50,50,50))
            img.save("Very Cool Image.png")
            await ctx.send(file=discord.File("Very Cool Image.png"))
            os.remove("Very Cool Image.png")


    @thank.error
    async def thank_error(self, ctx, error):
        await ctx.send('You need to enter a valid user to thank!')

    @commands.command(name='oopsie')
    async def oopsie(self, ctx, *, userName: discord.Member=None):
        if (not userName):
            embed = discord.Embed(description='Who did an oopsie?', color=63458)
            await ctx.send(embed=embed)
            return
        else:
            embed = discord.Embed(description=userName.mention + ' did an oopsie!', color=63458)
            await ctx.send(embed=embed)

    @oopsie.error
    async def oopsie_error(self, ctx, error):
        await ctx.send('{}, you did an oopsie by mentioning an invalid user!'.format(ctx.author.mention))


    @commands.command(name='poll')
    async def poll(self, ctx, contents, *options):
        if len(options)>10:
            return await ctx.send("You can only add up to 10 options")
        embed = discord.Embed(title=f'New poll by {ctx.author}', description="", color=63458)
        contents=f"​\n**{contents}**\n"
        for num, option in enumerate(options, 1):
            contents=f"\n{contents}\n**{num}.** {option}"
        embed.description=contents
        self.msg = await ctx.send(embed=embed)
        for i in range(len(options)):
            if i==9:
                await self.msg.add_reaction(self.emoji_reactions[1])
            else:
                await self.msg.add_reaction(self.emoji_reactions[0].format(i+1))
        await ctx.message.delete()

    @poll.error
    async def poll_error(self, ctx, error):
        embed = discord.Embed(title='Usage', description='`+poll "question" <Options in quotes> Ex: "Option1" "Option2" "Option3"`\nYou can add up to 10, separated by a space.', color=63458)
        await ctx.send(embed=embed)
        try:
            await self.msg.delete()
        except:
            pass

    @commands.command(name='giveaway')
    async def giveaway(self, ctx, time, *, prize):
        if not ctx.author.guild_permissions.administrator:
                await ctx.send("You do not have permission to start giveaways")
                return
        if time[-1:].lower()=="m":
            timeScale=float(time[:-1])*60
            extra="minutes"
            if time[:-1] =="1":
                extra="minute"
            text=f"{time[:-1]} {extra}"
        elif time[-1:].lower()=="h":
            timeScale=float(time[:-1])*60*60
            extra="hours"
            if time[:-1] =="1":
                extra="hour"
            text=f"{time[:-1]} {extra}"
        elif time[-1:].lower()=="d":
            timeScale=float(time[:-1])*60*60*24
            extra="days"
            if time[:-1] =="1":
                extra="day"
            text=f"{time[:-1]} {extra}"
        embed = discord.Embed(title='Giveaway!\nReact with :tada: to enter!', description=prize, color=63458)
        embed.set_footer(text=f'Ends in {text}')
        startGiveaway = await ctx.send(embed=embed)
        await startGiveaway.add_reaction(u"\U0001F389")
        await ctx.message.delete()
        await asyncio.sleep(timeScale)
        entries=None
        winner=None
        newGiveawayMsg = await ctx.channel.fetch_message(startGiveaway.id)
        react=newGiveawayMsg.reactions
        for item in react:
            if str(item.emoji)=="🎉":
                entries=await item.users().flatten()
        winner=random.choice(entries)
        while winner == self.bot.user:
            winner=random.choice(entries)
        await ctx.send(f'''**Giveaway ended**
Congratulations, {winner.mention}, you won **{prize}**!''')

    @giveaway.error
    async def giveaway_error(self, ctx, error):
        embed=discord.Embed(color=63458)
        embed.add_field(name="Usage", value="""**giveaway <number of days> <prize>**
Giveaways will be drawn automatically after the specified number of days""")
        await ctx.send(embed=embed)
        try:
            await startGiveaway.delete()
        except:
            pass


    @commands.command(name='youtube', aliases =["yt"])
    async def youtube(self, ctx, channel):
        if "http://" in channel or "https://" in channel or "www." in channel or "youtube.com" in channel or "youtu.be" in channel or "/channel/" in channel or "/c/" in channel or "/user/" in channel:
            channel=channel.strip("http://")
            channel=channel.strip("https://")
            channel=channel.strip("www.")
            channel=channel.strip("youtube.com")
            channel=channel.strip("youtu.be")
            channel=channel.strip("/channel/")
            channel=channel.strip("/c/")
            channel=channel.strip("/user/")
            if channel[:-1]=="/":
                channel=channel.strip("/")
            stats_for="id"
        else:
            stats_for="forUsername"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&{stats_for}={channel}&key={self.bot.gapi}") as resp:
                info=await resp.text()
        try:
            data = json.loads(info)['items'][0]
        except:
            return await ctx.send("Couldn't find that channel!")
        stats=data["statistics"]
        channel_id=data["id"]
        embed=discord.Embed(title=f"Statistics for {channel}", description=f"[Visit channel](https://youtube.com/channel/{channel_id})", color=63458)
        embed.add_field(name="Subscribers", value="{:,d}".format(int(stats["subscriberCount"])))
        embed.add_field(name="Videos", value="{:,d}".format(int(stats["videoCount"])))
        embed.add_field(name="Total views", value="{:,d}".format(int(stats["viewCount"])))
        await ctx.send(embed=embed)

    @youtube.error
    async def youtube_error(self, ctx, error):
        await ctx.send("You didn't specify the channel to get the stats for!")

    @commands.command(name="dog")
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as resp:
                data=await resp.text()
        info=json.loads(data)["message"]
        embed=discord.Embed(color=63458)
        embed.add_field(name="Here is your random dog", value=f"[Link to download image]({info})")
        embed.set_image(url=info)
        await ctx.send(embed=embed)

    @commands.command(name="vote")
    async def vote(self, ctx):
        embed=discord.Embed(title="Upvote me on Discord Bot List",  description="""[Click here to vote!](https://discordbots.org/bot/541679937870888986/vote)
After you've voted, use `claim` to get 20 bonus credits!""", color=63458)
        embed.set_thumbnail(url=ctx.me.avatar_url_as(static_format="png"))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))
