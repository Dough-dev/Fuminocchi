import discord
from discord.ext import commands
import asyncio
import json

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            with open("required files/autorole.json", "r") as f:
                data=json.load(f)
            roles=data[str(member.guild.id)]
            for role in roles:
                roleObject=discord.utils.get(member.guild.roles, id=role)
                await member.add_roles(roleObject)
        except:
            pass

    @commands.command(name='join', aliases=["role", "joinrole"])
    async def join(self, ctx, *, role=None):
        if (not role):
            await ctx.send("You haven't specified which role you want to join.")
            return
        with open("required files/roles.json", "r") as f:
            roles=json.load(f)
        for guildRole in ctx.guild.roles:
            if role.lower() in str(guildRole.name).lower():
                if guildRole.id in roles[str(ctx.guild.id)]["roles"]:
                    roleUser=ctx.author
                    joinedRole=discord.utils.get(ctx.guild.roles, name=str(guildRole.name))
                    await roleUser.add_roles(joinedRole)
                    await ctx.send("You have joined **{}**".format(str(guildRole.name)))
                    return
        else:
            await ctx.send("That's not a valid role.")

    @join.error
    async def join_error(self, ctx, error):
        await ctx.send("There was a problem. Either this guild doesn't have any assignable roles, the requested role is higher than my highest role, or I don't have permission.")

    @commands.command(name='leave', aliases=["leaverole"])
    async def leave(self, ctx, *, role:str=None):
        if (not role):
            await ctx.send("You haven't specified which role you want to leave.")
            return
        with open("required files/roles.json", "r") as f:
            roles=json.load(f)
        for guildRole in ctx.guild.roles:
            if role.lower() in str(guildRole.name).lower():
                if guildRole.id in roles[str(ctx.guild.id)]["roles"]:
                    roleUser=ctx.author
                    joinedRole=discord.utils.get(ctx.guild.roles, name=str(guildRole.name))
                    await roleUser.remove_roles(joinedRole)
                    await ctx.send("You have left **{}**".format(str(guildRole.name)))
                    return
        else:
            await ctx.send("That's not a valid role.")

    @leave.error
    async def leave_error(self, ctx, error):
        await ctx.send("There was a problem. Either this guild doesn't have any assignable roles, the requested role is higher than my highest role, or I don't have permission.")


    @commands.command(name="roles", aliases=["ranks"])
    async def roles(self, ctx):
        with open("required files/roles.json", "r") as f:
            roles=json.load(f)
        rolesMessage=""
        try:
            for roleID in roles[str(ctx.guild.id)]["roles"]:
                roleInfo=discord.utils.get(ctx.guild.roles, id=roleID)
                roleName=roleInfo.name
                rolesMessage+=roleName+"\n"
            embed=discord.Embed(color=63458)
            embed.add_field(name="Assignable roles", value=rolesMessage)
            return await ctx.send(embed=embed)
        except:
            await ctx.send("This guild doesn't have any assignable roles.")

    @commands.command(name="autorole", aliases=["ar"])
    async def autorole(self, ctx, action=None, *, name=None):
        if not action:
            with open("required files/autorole.json", "r") as f:
                dict=json.load(f)
            if str(ctx.guild.id) not in dict:
                return await ctx.send("This guild doesn't have any autoroles!")
            else:
                desc=""
                for roleID in dict[str(ctx.guild.id)]:
                    role=discord.utils.get(ctx.guild.roles, id=roleID)
                    desc+=role.name+"\n"
                embed=discord.Embed(title="Autoroles", description=desc, color=63458)
                return await ctx.send(embed=embed)
        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You don't have permission to change autorole settings!")
        with open("required files/autorole.json", "r") as f:
            dict=json.load(f)
        if action.lower()=="add":
            newRole=discord.utils.get(ctx.guild.roles, name=name)
            if not newRole:
                return await ctx.send("Can't find that role. Make sure you typed the name exactly.")
            id = newRole.id
            if not str(ctx.guild.id) in dict:
                dict[str(ctx.guild.id)]=[]
                with open("required files/autorole.json", "w") as f:
                    json.dump(dict, f)
            with open("required files/autorole.json", "r") as f:
                dict=json.load(f)
            if id not in dict[str(ctx.guild.id)]:
                dict[str(ctx.guild.id)].append(id)
                with open("required files/autorole.json", "w") as f:
                    json.dump(dict, f)
                await ctx.send(f"**{newRole.name}** will be added to every member when they join.")
            else:
                return await ctx.send(f"**{newRole.name}** is already an autorole!")
        elif action.lower()=="remove":
            noRole=discord.utils.get(ctx.guild.roles, name=name)
            if not noRole:
                return await ctx.send("Can't find that role. Make sure you typed the name exactly.")
            id = noRole.id
            if not str(ctx.guild.id) in dict:
                await ctx.send("This guild doesn't have any autoroles!")
            elif noRole.id not in dict[str(ctx.guild.id)]:
                await ctx.send(f"**{noRole.name}** isn't an autorole!")
            else:
                dict[str(ctx.guild.id)].remove(id)
                with open("required files/autorole.json", "w") as f:
                    json.dump(dict, f)
                await ctx.send(f"**{noRole.name}** is no longer an autorole")
        else:
            embed=discord.Embed(title="Usage", description="`autorole add/remove role_name`\nExample: `autorole add Members` to add the 'Members' roles to autorole, `autorole remove People` stops the 'People' roles being automatically added, `autorole` shows you all the autoroles.\nMake sure you type the role name exactly right.", color=63458)
            await ctx.send(embed=embed)

    @autorole.error
    async def autorole_error(self, ctx, error):
        embed=discord.Embed(title="Usage", description="`autorole add/remove role_name`\nExample: `autorole add Members` to add the 'Members' roles to autorole, `autorole remove People` stops the 'People' roles being automatically added, `autorole` shows you all the autoroles.\nMake sure you type the role name exactly right.", color=63458)
        await ctx.send(embed=embed)





def setup(bot):
    bot.add_cog(Roles(bot))
