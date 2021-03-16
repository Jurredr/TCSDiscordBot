import discord
from discord.ext import commands
from docstring_parser import Style
from docstring_parser import parse as parse_docstring

from cogs.utils.smth import *
from globalfuncs import *


async def prefix(_, message):
    return commands.when_mentioned_or('?')(_, message)


class HelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(
            **options,
            show_hidden=False,
            command_attrs={
                'cooldown': commands.Cooldown(2, 5.0, commands.BucketType.user)
            }
        )

    def construct_embed(self, title: str = None, description: str = None):
        return discord.Embed(
            title=title,
            description=description,
            colour=discord.Colour.teal()
        )

    def get_docs(self, command):
        if docs := command.help:
            if docs := parse_docstring(docs, style=Style.numpydoc):
                return docs

    def get_prefixed_command(self, command, bold=True):
        return ('**%s%s**' if bold else '%s%s') % (self.clean_prefix, command.qualified_name)

    def get_command_signature(self, command):
        return ('**%s%s** %s' % (self.clean_prefix, command.qualified_name, '*' + command.signature + '*' if command.signature else '')).strip()

    def add_indented_commands(self, commands, *, heading=None, max_size=None):
        if not commands:
            return

        entries = list()
        for command in commands:
            entries.append(
                f'• {self.get_command_signature(command)}' + (f' — {command.short_doc}' if command.short_doc else '')
            )

        return entries

    async def send_bot_help(self, mapping):
        embed = self.construct_embed(title="Help")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No category")
                embed.add_field(name=cog_name, value='\n'.join(self.add_indented_commands(filtered)), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)
        embed = self.construct_embed(
            title='Group: ' + self.get_prefixed_command(group),
            description='\n'.join(self.add_indented_commands(filtered))
        )
        if help_text := group.help:
            embed.add_field(name="Description", value=help_text)
        if alias := group.aliases:
            embed.add_field(name="Aliases", value=backtick('`, `'.join(alias)))

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = self.construct_embed(title='Command ' + self.get_prefixed_command(command))
        if docs := self.get_docs(command):
            embed.add_field(
                name='Description',
                value=docs.long_description if docs.long_description else docs.short_description
            )
            if cooldown := command._buckets._cooldown:
                embed.add_field(
                    name='Cooldown',
                    value=f"{cooldown.rate} command per {int(cooldown.per)} seconds"
                )
            embed.add_field(
                name='Usage',
                value=self.get_command_signature(command),
                inline=False
            )
            if docs.params:
                embed.add_field(
                    name='Arguments',
                    value='\n'.join([f"• **{param.arg_name}** — {param.description}" for param in docs.params]),
                    inline=False
                )
            if docs.meta != docs.params:
                meta = docs.meta
                if meta[-1].args[0] == 'examples':
                    examples = meta[-1]
                    embed.add_field(
                        name='Examples',
                        value='\n'.join([
                            '%s %s' % (self.get_prefixed_command(command, bold=False), example)
                            for example in examples.description.splitlines()
                        ])
                    )

        alias = command.aliases
        if alias:
            embed.add_field(name='Aliases', value=backtick("`, `".join(alias)), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        return


bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
    activity=discord.Game(name='?help'),
    help_command=HelpCommand(),
    owner_ids=MY_ID
)


@bot.event
async def on_ready():
    print(log_time() + 'Bot started')
    print('Connected as: ' + str(bot.user))
    print('Connected servers:', *bot.guilds, sep='\n\t', end='\n')


bot.load_extension('cogs.bgtasks')
bot.load_extension('cogs.commands')
bot.load_extension('cogs.quotes')
bot.load_extension('cogs.fun')

print(log_time() + 'Bot is starting')
bot.run(BOT_TOKEN)
