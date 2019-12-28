import math
import re
import discord
import lavalink
import asyncio
import json
from discord.ext import commands

url_rx = re.compile('https?:\\/\\/(?:www\\.)?.+')  # noqa: W605

class MusicPlayer(lavalink.DefaultPlayer):
    def __init__(self, guild_id:int, node):
        super().__init__(guild_id, node)

    def add(self, requester: int, track: dict, index: int = None):
        if index is None:
            self.queue.append(AudioTrack.build_new_track(track, requester))
        else:
            self.queue.insert(index, AudioTrack.build_new_track(track, requester))

class AudioTrack(lavalink.AudioTrack):

    @classmethod
    def build_new_track(cls, track, requester, extras:dict=None):
        """Returns an optional AudioTrack with artwork."""
        new_track=cls(requester)
        try:
            new_track.track = track['track']
            new_track.identifier = track['info']['identifier']
            new_track.is_seekable = track['info']['isSeekable']
            new_track.author = track['info']['author']
            new_track.duration = track['info']['length']
            new_track.stream = track['info']['isStream']
            new_track.title = track['info']['title']
            new_track.uri = track['info']['uri']
            new_track.artwork = track['info'].get('artwork', '')
            new_track.extra = extras or {}

            return new_track
        except KeyError:
            raise lavalink.InvalidTrack('An invalid track was passed.')


class MusicException(Exception):
    pass

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id, 1, None, MusicPlayer)
            bot.lavalink.add_node('127.0.0.1', 8080, 'youshallnotpass', 'us', 'default-node')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        bot.lavalink.add_event_hook(self.track_hook)
        print("Initialised Lavalink client")

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def track_hook(self, event):

        if isinstance(event, lavalink.events.TrackEndEvent):
            try:
                player=event.player
                player.store("previous", event.track.identifier)
            except:
                pass
        if isinstance(event, lavalink.events.TrackStartEvent):
            player=event.player
            requesterSong=await self.bot.fetch_user(int(event.track.requester))
            requesterName=requesterSong.name
            dur=None
            if not player.current.stream:
                dur = lavalink.utils.format_time(event.track.duration)
            else:
                dur="Livestream"
            if player.fetch("np"):
                try:
                    await player.fetch("np").delete()
                except:
                    pass

            embed = discord.Embed(color=65280, title='Now Playing')

            embed.description = f'[{player.current.title}]({player.current.uri})'
            embed.add_field(name='Uploaded by', value=f'{player.current.author}')
            embed.add_field(name="Duration", value=dur)
            embed.set_footer(text=f"Requested by {requesterName}")
            embed.set_thumbnail(url=event.track.artwork)
            channel=self.bot.get_channel(player.fetch("channel"))
            np=await channel.send(embed=embed)
            player.store("np", np)

        if isinstance(event, lavalink.events.TrackExceptionEvent):
            player=event.player
            channel=self.bot.get_channel(player.fetch("channel"))
            embed=discord.Embed(title="Something went wrong!", color=65280)
            embed.add_field(name="Error", value=event.exception)
            if player.fetch("np"):
                try:
                    await player.fetch("np").delete()
                except:
                    pass
            await channel.send(embed=embed)

        if isinstance(event, lavalink.TrackStuckEvent):
            player=event.player
            channel=self.bot.get_channel(player.fetch("channel"))
            await player.skip()
            if player.fetch("np"):
                try:
                    await player.fetch("np").delete()
                except:
                    pass
            await channel.send(f"{event.track.title} was skipped because there was a problem.")

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        player=self.bot.lavalink.players.get(guild_id)
        if player.repeat:
            player.repeat=not player.repeat
        if player.shuffle:
            player.shuffle=not player.shuffle
        await player.set_volume(100)
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    @commands.command(name="viewplaylist", aliases=["viewpl", "view"])
    async def viewplaylist(self, ctx, playlist_number, page=1):
        with open("required files/playlists.json", "r", encoding="utf8") as f:
            data=json.load(f)
        if str(ctx.author.id) not in data:
            return await ctx.send("You don't have any saved playlists!")
        embed=discord.Embed(color=65280)
        try:
            embed.title=data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["playlist_title"]
            embed.description=""
            if len(data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"])==0:
                return await ctx.send("This playlist is empty!")
            items_per_page = 10
            pages = math.ceil(len(data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"]) / items_per_page)
            start = (page - 1) * items_per_page
            end = start + items_per_page
            for index, track in enumerate(data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"][start:end], start=start):
                embed.description=f'{embed.description}`{index+1}.` [{track["song_title"]}]({track["song_link"]})\n'
            embed.set_footer(text=f'Page {page}/{pages} - {len(data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"])} songs')
            await ctx.send(embed=embed)
            return True
        except:
            await ctx.send("I can't find that number in your saved playlists!")
            return False

    @viewplaylist.error
    async def viewplaylist_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "viewplaylist")

    @commands.command(name="addsong", aliases=["add"])
    async def add_to_playlist(self, ctx, playlist_number, add_queue=None):
        player = self.bot.lavalink.players.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_playing:
            return await ctx.send("Nothing is playing right now!")

        with open("required files/playlists.json", "r", encoding="utf8") as f:
            data=json.load(f)
        if not add_queue or not add_queue=="queue":
            try:
                playlist_title=data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["playlist_title"]
                data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"].append({"song_title": player.current.title, "song_link": player.current.uri})
                with open("required files/playlists.json", "w", encoding="utf8") as f:
                    json.dump(data, f)
                return await ctx.send(f'`{player.current.title}` has been added to playlist `{playlist_title}`!  It is song number `{len(data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"])}`.')
            except:
                return await ctx.send("I couldn't find that number in your playlists!")
        else:
            try:
                playlist_title=data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["playlist_title"]
                for song in player.queue:
                    data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"].append({"song_title": song.title, "song_link": song.uri})
                with open("required files/playlists.json", "w", encoding="utf8") as f:
                    json.dump(data, f)
                return await ctx.send(f'Added `{len(player.queue)}` songs to `{playlist_title}`! This playlist has `{len(data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"])}` songs.')
            except:
                return await ctx.send("I couldn't find that number in your playlists!")

    @add_to_playlist.error
    async def addsong_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "addsong")

    @commands.command(name="createplaylist", aliases=["createpl"])
    async def create_playlist(self, ctx, *, title="Untitled playlist"):
        with open("required files/playlists.json", "r", encoding="utf8") as f:
            data=json.load(f)

        if str(ctx.author.id) not in data:
            data[str(ctx.author.id)]=[]
            data[str(ctx.author.id)].append({"playlist_info": {"playlist_title": title, "songs": []}})
        else:
            data[str(ctx.author.id)].append({"playlist_info": {"playlist_title": title, "songs": []}})
        with open("required files/playlists.json", "w", encoding="utf8") as f:
                    json.dump(data, f)
        return await ctx.send(f"`{title}` has been created! Its number is `{len(data[str(ctx.author.id)])}`. You can add songs to it using `addtoplaylist {len(data[str(ctx.author.id)])}`")

    @create_playlist.error
    async def createplaylist_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "createplaylist")

    @commands.command(name="deleteplaylist", aliases=["delplaylist", "deletepl", "delpl", "removeplaylist", "removepl", "rempl", "dpl", "rpl"])
    async def remove_playlist(self, ctx, playlist_number):
        if not await ctx.invoke(self.bot.get_command("viewplaylist"), playlist_number):
            return
        def check(m):
            if m.author==ctx.author and m.channel==ctx.channel:
                return m.content.lower()=="yes" or m.content.lower()=="no"
            return False
        embed=discord.Embed(title="Are you sure you want to delete this playlist?", description="Say yes/no\nThis cannot be undone!", color=65280)
        await ctx.send(embed=embed)
        try:
            msg=await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Removing playlist timed out.")
        if msg.content.lower()=="yes":
            with open("required files/playlists.json", "r", encoding="utf8") as f:
                data=json.load(f)
            removed=data[str(ctx.author.id)].pop(int(playlist_number)-1)
            title=removed["playlist_info"]["playlist_title"]
            with open("required files/playlists.json", "w", encoding="utf8") as f:
                json.dump(data, f)
            return await ctx.send(f"`{title}` has been removed.")
        else:
            return await ctx.send("Alright, the playlist has not been deleted.")

    @remove_playlist.error
    async def deleteplaylist_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "deleteplaylist")

    @commands.command(name="deletesong", aliases=["removesong", "delsong", "remsong"])
    async def delete_song(self, ctx, playlist_number, song_number:int):
        with open("required files/playlists.json", "r", encoding="utf8") as f:
            data=json.load(f)
        if str(ctx.author.id) not in data or len(data[str(ctx.author.id)])==0:
            return await ctx.send("You don't have any saved playlists!")
        if not await ctx.invoke(self.bot.get_command("viewplaylist"), playlist_number):
            return
        def check(m):
            if m.author==ctx.author and m.channel==ctx.channel:
                return m.content.lower()=="yes" or m.content.lower()=="no"
            return False
        embed=discord.Embed(title=f'''Are you sure you want to remove this track?
{data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"][song_number-1]["song_title"]}''', description="Say yes/no\nThis cannot be undone!", color=65280)
        await ctx.send(embed=embed)
        try:
            msg=await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Removing song timed out.")
        if msg.content.lower()=="yes":
            with open("required files/playlists.json", "r", encoding="utf8") as f:
                data=json.load(f)
            removed=data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"].pop(song_number-1)
            title=removed["song_title"]
            with open("required files/playlists.json", "w", encoding="utf8") as f:
                json.dump(data, f)
            return await ctx.send(f'`{title}` has been removed from `{data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["playlist_title"]}`')
        else:
            return await ctx.send("Alright, the playlist has not been deleted.")

    @delete_song.error
    async def deletesong_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "deletesong")

    @commands.command(name="playlists", aliases=["pls"])
    async def show_all_playlists(self, ctx):
        with open("required files/playlists.json", "r", encoding="utf8") as f:
            data=json.load(f)
        if str(ctx.author.id) not in data or len(data[str(ctx.author.id)])==0:
            return await ctx.send("You don't have any saved playlists!")
        embed=discord.Embed(title="Saved playlists", description="", color=65280)
        total_songs=0
        for num, pl in enumerate(data[str(ctx.author.id)], 1):
            all_songs=pl["playlist_info"]["songs"]
            number_of_songs=len(all_songs)
            total_songs+=number_of_songs
            playlist_title=pl["playlist_info"]["playlist_title"]
            embed.description=f"{embed.description}`{num}.` **{playlist_title}** - {number_of_songs} songs\n"
        embed.set_footer(text=f"{total_songs} total songs")
        await ctx.send(embed=embed)

    @show_all_playlists.error
    async def playlists_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "playlists")


    @commands.command(name="playlist", aliases=["plist", "pl"])
    async def pl(self, ctx, playlist_number):
        """Adds a user's custom playlist to the queue"""
        player = self.bot.lavalink.players.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        with open("required files/playlists.json", "r", encoding="utf8") as f:
            data=json.load(f)
        try:
            playlist_title=data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["playlist_title"]
            songs=data[str(ctx.author.id)][int(playlist_number)-1]["playlist_info"]["songs"]
        except:
            return await ctx.send("I couldn't find that playlist!")

        if not player.is_connected:
            if ctx.author.voice:
                permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                if not permissions.connect or not permissions.speak:  # Check user limit too?
                    return await ctx.send('I need the `CONNECT` and `SPEAK` permissions to play music!')


                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                return await ctx.send("You aren't connected to a voice channel!")

        if not ctx.author.voice:
            return await ctx.send("You aren't connected to a voice channel!")
        await asyncio.sleep(0.5)
        for i in range(7):
            if not ctx.me.voice:
                if i==4:
                    await ctx.author.voice.channel.connect()
                elif i==6:
                    return await ctx.send("Connecting to voice channel timed out")
                await asyncio.sleep(1)
        if ctx.me.voice.channel.id != ctx.author.voice.channel.id:
            return await ctx.send("We aren't in the same voice channel!")

        player.store('channel', ctx.channel.id)

        for song in songs:
            query=song["song_link"]
            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                return await ctx.send('Nothing found!')
            track = results['tracks'][0]

            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()
        await ctx.send(f"Added `{playlist_title}` to the queue!")

    @pl.error
    async def playlist_error(self, ctx, error):
        await ctx.invoke(self.bot.get_command("help"), "playlist")

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        player = self.bot.lavalink.players.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.

        if not player.is_connected:
            if ctx.author.voice:
                permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                if not permissions.connect or not permissions.speak:  # Check user limit too?
                    return await ctx.send('I need the `CONNECT` and `SPEAK` permissions to play music!')


                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                return await ctx.send("You aren't connected to a voice channel!")
        searching=await ctx.send(f"<:youtube:598562151556317207> Searching **\"{query.strip('<>')}\"**")
        player.store('searching', searching)
        if not ctx.author.voice:
            await player.fetch('searching').delete()
            return await ctx.send("You aren't connected to a voice channel!")
        await asyncio.sleep(0.5)
        for i in range(7):
            if not ctx.me.voice:
                if i==4:
                    await ctx.author.voice.channel.connect()
                elif i==6:
                    return await ctx.send("Connecting to voice channel timed out")
                await asyncio.sleep(1)
        if ctx.me.voice.channel.id != ctx.author.voice.channel.id:
            await player.fetch('searching').delete()
            return await ctx.send("We aren't in the same voice channel!")

        player.store('channel', ctx.channel.id)

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(color=65280)

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Added a playlist to the queue'
            embed.description = f'{results["playlistInfo"]["name"]} with {len(tracks)} songs'
        else:
            track = results['tracks'][0]
            pos=None
            if len(player.queue)==0:
                pos="Next up (position 1)"
            else:
                pos = len(player.queue)+1
            dur=None
            if track["info"]["isStream"]:
                dur="Livestream"
            else:
                dur = lavalink.utils.format_time(track["info"]["length"])
            est_duration=0
            for song in player.queue:
                est_duration+=song.duration
            if player.is_playing:
                est_duration+=(player.current.duration-player.position)
            if est_duration==0:
                est="Playing now"
            else:
                est=lavalink.utils.format_time(est_duration)
            embed.title = 'Added to queue'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            embed.add_field(name='Uploaded by', value=f'{track["info"]["author"]}')
            embed.add_field(name='Duration', value=f'{dur}')
            embed.add_field(name='Position in queue', value=f'{pos}')
            embed.add_field(name='Time until playing', value=f'{est}')
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            embed.set_thumbnail(url=f'{track["info"]["artwork"]}')
            player.add(requester=ctx.author.id, track=track)
        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command(name="playnow")
    async def playnow(self, ctx, *, query:str):
        player = self.bot.lavalink.players.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.queue and not player.is_playing:
            return await ctx.invoke(self.play, query=query)

        if not player.is_connected:
            if ctx.author.voice:
                permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                if not permissions.connect or not permissions.speak:  # Check user limit too?
                    return await ctx.send('I need the `CONNECT` and `SPEAK` permissions to play music!')


                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                return await ctx.send("You aren't connected to a voice channel!")
        searching=await ctx.send(f"<:youtube:598562151556317207> Searching **\"{query.strip('<>')}\"**")
        player.store('searching', searching)
        if not ctx.author.voice:
            await player.fetch('searching').delete()
            return await ctx.send("You aren't connected to a voice channel!")
        await asyncio.sleep(0.5)
        for i in range(7):
            if not ctx.me.voice:
                if i==4:
                    await ctx.author.voice.channel.connect()
                elif i==6:
                    return await ctx.send("Connecting to voice channel timed out")
                await asyncio.sleep(1)
        if ctx.me.voice.channel.id != ctx.author.voice.channel.id:
            await player.fetch('searching').delete()
            return await ctx.send("We aren't in the same voice channel!")
        if not ctx.author.guild_permissions.kick_members:
            if len(ctx.author.voice.channel.members) <= 2:
                pass
            else:
                return await ctx.send("You can't jump the queue whilst other people are in the voice channel!")

        player.store('channel', ctx.channel.id)

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await self.bot.lavalink.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        tracks = results['tracks']
        track = tracks.pop(0)
        if results['loadType'] == 'PLAYLIST_LOADED':
            for _track in tracks:
                player.add(requester=ctx.author.id, track=_track)
        else:
            player.add(requester=ctx.author.id, track=track, index=0)


        if player.shuffle:
            player.shuffle=not player.shuffle
            await player.stop()
            await player.play()
            player.shuffle=not player.shuffle
        else:
            await player.stop()
            await player.play()

    @commands.command(name="prev", aliases=["previous", "back"])
    async def prev(self, ctx):
        player=self.bot.lavalink.players.get(ctx.guild.id)
        try:
            if not ctx.author.guild_permissions.kick_members:
                if ctx.author.voice.channel.id != int(player.channel_id):
                    return await ctx.send("We aren't in the same voice channel!")
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                if len(isUserInVC)==2:
                    query = player.fetch("previous")

                    if not url_rx.match(query):
                        query = f'ytsearch:{query}'

                    results = await player.node.get_tracks(query)

                    if not results or not results['tracks']:
                        return await ctx.send('Nothing found!')

                    track = results['tracks'][0]
                    player.add(requester=ctx.author.id, track=track, index=0)

                else:
                    return await ctx.send("You can't do that whilst other people are in the voice channel!")
            else:

                query = player.fetch("previous")

                if not url_rx.match(query):
                    query = f'ytsearch:{query}'

                results = await player.node.get_tracks(query)

                if not results or not results['tracks']:
                    return await ctx.send('Nothing found!')

                track = results['tracks'][0]
                player.add(requester=ctx.author.id, track=track, index=0)
            if player.shuffle:
                player.shuffle=not player.shuffle
                await player.stop()
                await player.play()
                player.shuffle=not player.shuffle
            else:
                await player.stop()
                await player.play()
        except:
            return await ctx.send("There isn't a previous track to play!")

    @commands.command(name="playat")
    async def playat(self, ctx, index:int):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not ctx.author.guild_permissions.kick_members:
            if ctx.author.voice.channel.id != int(player.channel_id):
                return await ctx.send("We aren't in the same voice channel!")
            VC= self.bot.get_channel(int(player.channel_id))
            isUserInVC=VC.members
            if len(isUserInVC)==2:
                if index>len(player.queue)+1:
                    return await ctx.send("The queue isn't that long!")
                else:
                    for i in range(index-1):
                        del player.queue[0]
            else:
                return await ctx.send("You can't jump the queue while other people are in the voice channel.")
        else:
            if index>len(player.queue)+1:
                return await ctx.send("The queue isn't that long!")
            else:
                for i in range(index-1):
                    del player.queue[0]

        if player.shuffle:
            player.shuffle=not player.shuffle
            await player.stop()
            await player.play()
            player.shuffle=not player.shuffle
        else:
            await player.stop()
            await player.play()



    @commands.command()
    async def seek(self, ctx, *, seconds: str):
        """ Seeks to a given position in a track. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if not seconds:
            return await ctx.send('You need to specify the time to seek to')

        seconds=int(seconds)

        track_time = seconds * 1000
        await player.seek(track_time)
        await ctx.send(f'Moved track to **{lavalink.utils.format_time(track_time)}**')

    @commands.command(aliases=['forceskip', 's'])
    async def skip(self, ctx):
        """ Skips the current track. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not ctx.author.guild_permissions.kick_members:
            if ctx.author.id != int(player.current.requester):
                await ctx.send("You don't have permission to skip this song.")
                return

        if not player.is_playing:
            return await ctx.send('Nothing is playing right now!')

        await ctx.send('⏭')
        await player.skip()


    @commands.command(aliases=['np', 'n', 'playing'])
    async def now(self, ctx):
        """ Shows some stats about the currently playing song. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.current:
            return await ctx.send('Nothing playing.')

        positiontxt="Livestream"

        if not player.current.stream:
            position = lavalink.utils.format_time(player.position)
            duration = lavalink.utils.format_time(player.current.duration)
            positiontxt=f"{position}/{duration}"


        requesterSong=await self.bot.fetch_user(int(player.current.requester))
        requesterName=requesterSong.name

        embed = discord.Embed(color=65280, title='Now Playing')

        embed.description = f'[{player.current.title}]({player.current.uri})'
        embed.add_field(name='Uploaded by', value=f'{player.current.author}')
        embed.add_field(name='Position', value=f'{positiontxt}')

        embed.set_footer(text=f"Requested by {requesterName}")
        embed.set_thumbnail(url=f'{player.current.artwork}')

        await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        """ Shows the player's queue. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('The queue is empty!')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        est_duration=0
        for track in player.queue:
            est_duration+=track.duration
        est=lavalink.utils.format_time(est_duration)
        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=65280, title=f"{len(player.queue)} songs in the queue",
                              description=f'{queue_list}Estimated length: {est}')
        embed.set_footer(text=f'Page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(aliases=['resume'])
    async def pause(self, ctx):
        """ Pauses/Resumes the current track. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing is playing right now')

        if ctx.author.guild_permissions.kick_members:
            if player.paused:
                await player.set_pause(False)
                return await ctx.send(":arrow_forward:")
            else:
                await player.set_pause(True)
                return await ctx.send(":pause_button:")

        if player.paused:
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                if len(isUserInVC)==2:
                    for VCmember in isUserInVC:
                        if VCmember.id==ctx.author.id:
                            await player.set_pause(False)
                            return await ctx.send(':arrow_forward:')
                else:
                    await ctx.send("You can't pause songs whilst other people are in the voice channel.")
            else:
                await ctx.send("We aren't in the same voice channel")

        else:
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                if len(isUserInVC)==2:
                    for VCmember in isUserInVC:
                        if VCmember.id==ctx.author.id:
                            await player.set_pause(True)
                            return await ctx.send(':pause_button:')
                else:
                    await ctx.send("You can't pause songs whilst other people are in the voice channel.")
            else:
                await ctx.send("We aren't in the same voice channel")

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, volume: int = None):
        """ Changes the player's volume (0-200). """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not ctx.author.guild_permissions.kick_members:
            return await ctx.send("Only a moderator can change the volume")

        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')

        if volume > 200:
            return await ctx.send(f"{volume}% is too high")
        elif volume <1:
            return await ctx.send(f"{volume}% is too low")

        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command()
    async def shuffle(self, ctx):
        """ Shuffles the player's queue. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        if ctx.author.guild_permissions.kick_members:
            player.shuffle = not player.shuffle
            return await ctx.send('🔀 ' + ('Enabled' if player.shuffle else 'Disabled'))

        if str(player.shuffle)=="False":
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                if len(isUserInVC)==2:
                    for VCmember in isUserInVC:
                        if VCmember.id==ctx.author.id:
                            player.shuffle = not player.shuffle
                            return await ctx.send('🔀 ' + ('Enabled' if player.shuffle else 'Disabled'))
                else:
                    await ctx.send("You can't shuffle songs whilst other people are in the voice channel.")
            else:
                await ctx.send("We aren't in the same voice channel")
        else:
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                for VCmember in isUserInVC:
                    if VCmember.id==ctx.author.id:
                        player.shuffle = not player.shuffle
                        return await ctx.send('🔀 ' + ('Enabled' if player.shuffle else 'Disabled'))
            else:
                await ctx.send("We aren't in the same voice channel")

    @commands.command(aliases=['loop'])
    async def repeat(self, ctx):
        """ Repeats the current song until the command is invoked again. """
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        if ctx.author.guild_permissions.kick_members:
            player.repeat = not player.repeat
            return await ctx.send('🔁 ' + ('Enabled' if player.repeat else 'Disabled'))


        if str(player.repeat)=="False":
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                if len(isUserInVC)==2:
                    for VCmember in isUserInVC:
                        if VCmember.id==ctx.author.id:
                            player.repeat = not player.repeat
                            return await ctx.send('🔁 ' + ('Enabled' if player.repeat else 'Disabled'))
                else:
                    await ctx.send("You can't repeat songs whilst other people are in the voice channel.")
            else:
                await ctx.send("We aren't in the same voice channel")
        else:
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                for VCmember in isUserInVC:
                    if VCmember.id==ctx.author.id:
                        player.repeat = not player.repeat
                        return await ctx.send('🔁 ' + ('Enabled' if player.repeat else 'Disabled'))
            else:
                await ctx.send("We aren't in the same voice channel")

    @commands.command()
    async def remove(self, ctx, index: int):
        """ Removes an item from the player's queue with the given index. """
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Nothing queued.')
        if index > len(player.queue) or index < 1:
            return await ctx.send(f'Number needs to be between 1 and {len(player.queue)}')
        index -= 1
        if not ctx.author.guild_permissions.kick_members:
            removeRequester=player.queue[index]
            if ctx.author.id != int(removeRequester.requester):
                await ctx.send("You don't have permission to remove songs from thr queue")
                return
        removed = player.queue.pop(index)
        await ctx.send(f'Removed **{removed.title}** from the queue.')

    @commands.command(name="move")
    async def move(self, ctx, original:int=None, new:int=None):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if ctx.author.guild_permissions.kick_members:
            try:
                original-=1
                new-=1
                player.queue.insert(new, player.queue.pop(original))
                await ctx.send(f"Moved {player.queue[new].title} to position {new+1}")
            except Exception as e:
                return await ctx.send(f"""Couldn't move items```{e}```""")


    @commands.command()
    async def search(self, ctx, *, query):
        """ Lists the first 10 search results from a given query. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found.')

        tracks = results['tracks'][:10]  # First 10 results

        o = ''
        for index, track in enumerate(tracks, start=1):
            track_title = track['info']['title']
            track_uri = track['info']['uri']
            o += f'`{index}.` [{track_title}]({track_uri})\n'

        embed = discord.Embed(color=65280, description=o)
        await ctx.send(embed=embed)

    @commands.command(aliases=['stop', 'dc'])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send('I\'m not connected to a voice channel')

        if ctx.author.guild_permissions.kick_members:
            player.queue.clear()
            await player.stop()
            await self.connect_to(ctx.guild.id, None)
            return await ctx.send(':stop_button:  Cleared the queue and disconnected from voice channel')

        if ctx.author.voice:
            if ctx.author.voice.channel.id == int(player.channel_id):
                VC= self.bot.get_channel(int(player.channel_id))
                isUserInVC=VC.members
                if len(isUserInVC)==2:
                    for VCmember in isUserInVC:
                        if VCmember.id==ctx.author.id:
                            player.queue.clear()
                            await player.stop()
                            await self.connect_to(ctx.guild.id, None)
                            await ctx.send(':stop_button:  Cleared the queue and disconnected from voice channel')
                else:
                    return await ctx.send('I can\'t stop playing whilst other people are in the voice channel!')
            else:
                return await ctx.send('We aren\'t in the same voice channel!')
        else:
            VC= self.bot.get_channel(int(player.channel_id))
            VCmembers=VC.members
            if len(VCmembers)==1:
                player.queue.clear()
                await player.stop()
                await self.connect_to(ctx.guild.id, None)
                await ctx.send(':stop_button:  Cleared the queue and disconnected from voice channel')
            else:
                return await ctx.send('You aren\'t in a voice channel!')


    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        pass


def setup(bot):
    bot.add_cog(Music(bot))
    print("Loaded Music version 4")
