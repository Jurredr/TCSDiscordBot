from asyncio import sleep
from random import choice

import discord
from discord.ext import commands

from cogs.utils.smth import *
from uwuinator import uwuinator


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # not a real command, the real one uses all data about you and passes it through super smart machine learning mechanism
    @commands.command(aliases=['is_imposter', 'impostor', 'imposter'])
    async def is_impostor(self, ctx, user: discord.Member):
        """Check if sus user is an impostor
        """

        is_impostor = value_to_bool(user.id)

        embed = discord.Embed(
            title='Is an impostor' if is_impostor else 'Is a crewmate',
            colour=discord.Colour.dark_red() if is_impostor else discord.Colour(9305599)
        )
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_image(
            url='https://media.discordapp.net/attachments/815585601336246298/815585655203037254/impostor1.png'
            if is_impostor else 'https://media.discordapp.net/attachments/815585601336246298/815585653726380052/Crewmate1.png'
        )

        await ctx.reply(embed=embed, **rKW)

    @is_impostor.error
    async def on_impostor_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.reply('No sus user provided', **rKW)
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.reply("Couldn't find specified user", **rKW)
        else:
            raise error

    # fake command (the real one is much smarter ofc and gives real answers)
    @commands.command('8ball', aliases=['ball'])
    async def eight_ball(self, ctx):
        """
        Ask 8ball for an answer
        """
        answers = [
            # Affirmative
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes – definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            # Non-committal
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            # Negative
            "Don't count on it.",
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.'
        ]
        await ctx.trigger_typing()
        await sleep(3)
        # so basically here im using fine trained ai in choice function to get the most accurate answer
        # there is some smart ass logic behind this so don't dive deep
        await ctx.reply(f'*\U0001F3B1 says:* **{choice(answers)}**', mention_author=False)

    @commands.command('uwuinator', aliases=['uwuinate', 'uwu', 'uwuizer'])
    async def uwuinator_command(self, ctx, *, text: str):
        """
        Make text better

        Makes text definitely better by making it more uwu-like. owo

        Parameters
        ----------
        text :
            text to make better
        """
        try:
            uwud_text = uwuinator.uwuinate(text)
            embed = discord.Embed(
                title='here is ur text... uwu',
                description=uwud_text,
                colour=discord.Colour.random()
            )
        except:
            await ctx.reply("oopsie... somethimg wemt wromg... sowwy... >w<", **rKW)
        else:
            await ctx.send(embed=embed)

    @uwuinator_command.error
    async def on_uwu_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.reply("u haven't provided any text... ~w~", **rKW)
        else:
            raise error


def setup(bot):
    bot.add_cog(Fun(bot))
