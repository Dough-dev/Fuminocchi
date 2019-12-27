import discord
from discord.ext import commands

class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

#Events

#Commands
@commands.command()
async def uwu(self, ctx):
    await ctx.send('uwu')

def setup(client)
    client.add_cog(CogTest(client))
