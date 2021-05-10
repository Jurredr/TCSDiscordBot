import discord
from discord.ext import commands

from cogs.utils.smth import *


class Quotes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['cite'])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.user)
    async def quote(self, ctx: commands.Context):
        """Forward referenced message to <#756428576160481280> channel
        """
        if reference := ctx.message.reference:
            reference = reference.resolved
            if isinstance(reference, discord.Message):

                reference_cite = None
                if ref_reference := reference.reference:
                    if ref_reference.resolved:
                        ref_reference = ref_reference.resolved
                    else:
                        ref_reference = ref_reference.cached_message

                    if isinstance(ref_reference, discord.Message):
                        reference_cite = f'> {ref_reference.author.mention}\n> ' + ref_reference.content.replace('\n', '\n> ')[:2048] + '\n'

                embed = discord.Embed(
                    description=((reference_cite if reference_cite else '') + reference.content)[:2048],
                    colour=to_colour(reference.author.id),
                    timestamp=reference.created_at
                )
                embed.set_author(
                    name=str(reference.author),
                    icon_url=reference.author.avatar_url_as(static_format='png')
                )
                embed.add_field(name='Message link', value=f'[Link]({reference.jump_url})')
                msg = await self.bot.get_channel(QUOTES_CHANNEL).send(embed=embed)
                await ctx.message.add_reaction(SUCCESS_REACTION)
                await msg.add_reaction(self.bot.get_emoji(UPVOTE_REACTION_ID))
            else:
                await ctx.reply('Unsupported message type', **rKW)

    @quote.error
    async def on_quote_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply("Command is on cooldown", **rKW)
        else:
            raise error


def setup(bot):
    bot.add_cog(Quotes(bot))
