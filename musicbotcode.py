import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {"options": '-vn'}
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}

class MusicBOT(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("You're not in a voice channel!")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                try:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    await ctx.send(f"Added to queue: **{title}**")
                    print(f"Added to queue: {title}")
                except Exception as e:
                    await ctx.send(f"An error occurred while processing your request: {e}")
                    print(f"Error extracting info: {e}")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            try:
                print(f"Processing URL: {url}")  # Debug line
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(ctx)))
                await ctx.send(f'Now Playing **{title}**')
                print(f'Now Playing: {title}')
            except Exception as e:
                await ctx.send(f"Could not play the audio: {title} - Error: {e}")
                print(f"Error playing audio: {e}")
                await self.play_next(ctx)
        else:
            await ctx.send("Queue is empty")
            print("Queue is empty")
            if ctx.voice_client:
                await ctx.voice_client.disconnect()

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped!")
            print("Skipped!")

client = commands.Bot(command_prefix='!', intents=intents)

async def main():
    await client.add_cog(MusicBOT(client))
    await client.start("MAYANK'S_DISCORD_TOKEN")

asyncio.run(main())
