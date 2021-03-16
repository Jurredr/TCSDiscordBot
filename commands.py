import discord
from discord.ext import commands

from cogs.utils.smth import *


class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command('hours', aliases=['lc', 'lecture_hours'])
    async def lecture_hours(self, ctx):
        """Sends a table of UT lecture hours"""
        embed = discord.Embed(
            title='Lecture Hours',
            description='```' + ('\n'.join([f'{str(hour) + ":":<4}{get_time(times[0])} - {get_time(times[1])}' for hour, times in HOURS.items()])) + '```'
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Calculates delay of the bot"""
        pong = '\U0001F3D3 Pong!'
        ping_msg = await ctx.send(pong)
        ms = (ping_msg.created_at - ctx.message.created_at).total_seconds() * 1000
        await ping_msg.edit(content=f'{pong} `{int(ms)}ms`')

    @commands.command(aliases=['mu', 'top'])
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.user)
    async def most_upvoted(self, ctx, channel: discord.TextChannel):
        """Sends top of the most upvoted messages
        """
        if channel.guild == ctx.guild:
            bump_emoji_id = UPVOTE_REACTION_ID
            messages = dict()
            waiting_msg = await ctx.send('<a:discord_loading:590967589686214676> Parsing messages...')
            await ctx.trigger_typing()
            async for message in channel.history(limit=None, oldest_first=True):
                if message.reactions:
                    if bump_emoji_id in [reaction.emoji.id for reaction in message.reactions if isinstance(reaction.emoji, discord.Emoji)]:
                        for reaction in message.reactions:
                            if isinstance(reaction.emoji, discord.Emoji):
                                if reaction.emoji.id == bump_emoji_id:
                                    messages[message] = reaction.count
                                    break

            messages = {k: v for k, v in sorted(messages.items(), key=lambda item: item[1], reverse=True)}
            text = ''
            for message, bumps in messages.items():
                row = f'**{bumps}** <:{UPVOTE_REACTION_NAME}:{bump_emoji_id}> — [{message.created_at.strftime(MEETING_TIME_FORMAT)}]({message.jump_url}) ({message.author.mention})'  # TODO change bump emoji
                if len(text + row) > 2048:
                    break
                text += row + '\n'

            embed = discord.Embed(
                title='Most upvoted messages for #' + channel.name,
                colour=discord.Colour.dark_magenta(),
                description=text if text else 'No messages with upvotes found',
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f'Total upvotes: {sum(messages.values())}')
            await waiting_msg.delete()
            await ctx.send(embed=embed)

    @most_upvoted.error
    async def on_most_bumped_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("No channel provided", **rKW)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply("Command is on cooldown", **rKW)
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.reply("Another call of this command is already parsing", **rKW)
        elif isinstance(error, commands.errors.ChannelNotFound):
            await ctx.reply("Couldn't find provided channel", **rKW)
        else:
            raise error

    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.user)
    async def feedback(self, ctx, *, content: str):
        """Send feedback to the developer
        """
        e = discord.Embed(
            title='Feedback',
            colour=discord.Colour.dark_purple()
        )
        channel = self.bot.get_channel(815607403474452511)
        if channel is None:
            return

        e.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        e.description = '```' + content + '```'
        e.timestamp = ctx.message.created_at

        if ctx.guild is not None:
            e.add_field(name='Server', value=f'{ctx.guild.name} ||{ctx.guild.id}||', inline=False)

        e.add_field(name='Channel', value=f'{ctx.channel} ||{ctx.channel.id}||', inline=False)
        e.add_field(name='Author ID', value=f'||{ctx.author.id}||', inline=False)

        await channel.send(embed=e)
        await ctx.send(f'Successfully sent feedback')

    @feedback.error
    async def on_feedback_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("No feedback provided")
            self.feedback.reset_cooldown(ctx)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.reply("Command is on cooldown", **rKW)
        else:
            raise error


def setup(bot):
    bot.add_cog(Commands(bot))
