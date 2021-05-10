import re
from time import strptime as tstrptime

import bs4
import discord
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
from canvasapi import Canvas
from dateparser import parse as parse_date
from discord.ext import commands, tasks
from markdownify import MarkdownConverter, UNDERLINED, ATX_CLOSED

from cogs.utils.db import *
from cogs.utils.smth import *
from globalfuncs import *

EMBED_DESC_MAX_LENGTH = 2048

canvas = Canvas('https://canvas.utwente.nl', CANVAS_ACCESS_TOKEN)
schedule = AsyncIOScheduler()


def append_meetings(meetings: list):
    for meeting in meetings:
        try:
            Meetings.insert({
                Meetings.link: meeting["link"],
                Meetings.start_time: meeting["start_time"],
                Meetings.password: meeting["password"]
            }).execute()
        except peewee.IntegrityError:
            pass


class md(MarkdownConverter):
    def convert_hn(self, n, el, text, convert_as_inline):
        if convert_as_inline:
            return text

        style = self.options['heading_style']
        text = text.rstrip()
        if style == UNDERLINED and n <= 2:
            line = '=' if n == 1 else '-'
            return self.underline(text, line)
        hashes = '#' * n
        if style == ATX_CLOSED:
            return '%s %s %s\n\n' % (hashes, text, hashes)
        if style == 'discord':
            return f'`{text.strip()}`\n'
        return '%s %s\n\n' % (hashes, text)


def markdownify(html, **options):
    return md(**options).convert(html)


class Loop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.get_announcements.start()
        self.parse_zoom_links.start()
        self.last_post = None
        schedule.start()

    async def send_zoom_invite(self, link: str, password: Union[str, int]):
        channel = self.bot.get_channel(ZOOM_MEETINGS_CHANNEL)
        await channel.send(
            embed=discord.Embed(
                title='Zoom meeting right now',
                description=construct_zoom_link(link, password),
                timestamp=datetime.utcnow(),
                colour=discord.Colour.blue()
            ).add_field(
                name='Password',
                value=str(password)
            )
        )
        Meetings.update({Meetings.notified: True}).where(Meetings.link == link).execute()

    async def schedule_meetings(self):
        meetings = Meetings.select().where((Meetings.notified == False) & (Meetings.start_time > datetime.now()))
        meetings_times = [meeting.next_run_time for meeting in schedule.get_jobs()]
        for meeting in meetings:
            if meeting.start_time not in meetings_times:
                schedule.add_job(
                    self.send_zoom_invite,
                    args=(meeting.link, meeting.password),
                    trigger='date',
                    run_date=meeting.start_time,
                    id=meeting.link
                )

    @commands.is_owner()
    @commands.command('schedule_meetings', aliases=['sm'], hidden=True)
    async def manual_schedule_meetings(self, ctx):
        await self.schedule_meetings()
        await ctx.message.add_reaction(SUCCESS_REACTION)

    @commands.group(aliases=['meetings'])
    async def meeting(self, ctx):
        """Meetings management commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help('meeting')

    @meeting.command('list', aliases=['scheduled', 'all'])
    async def scheduled_meetings(self, ctx):
        """Show all scheduled meetings
        """
        embed = discord.Embed(
            title='Scheduled meetings'
        )

        for job in schedule.get_jobs():
            embed.add_field(
                name=job.next_run_time.strftime(MEETING_TIME_FORMAT),
                value=job.args[0],
                inline=False
            )

        if not embed.fields:
            embed.description = 'There are no scheduled meetings'

        await ctx.send(embed=embed)

    @meeting.command('add')
    @commands.has_guild_permissions(administrator=True)
    async def add_meeting(self, ctx, link, password: int, *, meeting_time):
        """
        Add a meeting to the schedule

        Adds a meeting with provided parameters to the schedule.

        Parameters
        ----------
        link :
            meeting invitation link
        password :
            password for the meeting
        meeting_time :
            meeting datetime. Month should be human-readable to be distinguishable

        Examples
        --------
        https://utwente-nl.zoom.us/j/1234567890 123456 01 march 2021 13:45
        """
        if link := re.match(ZOOM_LINK_REGEX, link):
            link = link[0]
            if not Meetings.select().where(Meetings.link.contains(link)).exists():
                if password := re.match(r'\d{6}', str(password)):
                    password = password[0]
                    if meeting_time := parse_date(meeting_time):
                        if meeting_time.time().hour and meeting_time.time().minute:
                            if meeting_time.year == 2021:
                                meeting_time = meeting_time.replace(second=0)
                                if meeting_time > datetime.now():
                                    if meeting_time not in [meeting.next_run_time for meeting in schedule.get_jobs()]:
                                        append_meetings([{
                                            'link': link,
                                            'start_time': meeting_time,
                                            'password': password
                                        }])
                                        await self.schedule_meetings()

                                        embed = discord.Embed(
                                            title='Meeting has been added successfully'
                                        )
                                        embed.add_field(name='Link', value=link)
                                        embed.add_field(name='Meeting time', value=meeting_time.strftime(MEETING_TIME_FORMAT))
                                        embed.add_field(name='Password', value=password)

                                        await ctx.send(embed=embed)
                                    else:
                                        await ctx.reply('There is already a meeting at this time', **rKW)
                                else:
                                    await ctx.reply("Meeting cannot be scheduled in the past", **rKW)
                            else:
                                await ctx.reply(f"I don't think you really meant {meeting_time.year} year", **rKW)
                        else:
                            await ctx.reply("Time is not specified", **rKW)
                    else:
                        await ctx.reply('Could not parse provided meeting time', **rKW)
                else:
                    await ctx.reply('Provided password is incorrect', **rKW)
            else:
                await ctx.reply('Meeting with specified link already exists', **rKW)
        else:
            await ctx.reply("Provided zoom link is incorrect", **rKW)

    @add_meeting.error
    async def on_add_meeting_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.BadArgument):
            await ctx.reply(
                f"You haven't specified one of the required arguments or one of the specified arguments is incorrect. Type `{(await self.bot.get_prefix(ctx))[-1]}help {ctx.command.qualified_name}`",
                **rKW
            )
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply("You don't have permissions to run this command", **rKW)
        else:
            raise error

    @meeting.command('remove', aliases=['rm', 'del'])
    @commands.has_guild_permissions(administrator=True)
    async def remove_meeting(self, ctx, link: str):
        """
        Remove meeting from schedule

        Removes meeting from the schedule and marks it as notified.

        Parameters
        ----------
        link :
            link of the meeting
        
        Examples
        --------
        https://utwente-nl.zoom.us/j/1234567890
        """
        if link := re.match(ZOOM_LINK_REGEX, link):
            link = link[0]
            if Meetings.select().where(Meetings.link.contains(link)).exists():
                try:
                    schedule.remove_job(link)
                    Meetings.update({Meetings.notified: True}).where(Meetings.link.contains(link)).execute()
                except JobLookupError:
                    await ctx.reply("Couldn't find specified meeting in scheduled", **rKW)
                except Exception as error:
                    await ctx.reply("Error has occurred", **rKW)
                    raise error
                else:
                    await ctx.reply("Meeting has been successfully removed", **rKW)
        else:
            await ctx.reply("Couldn't find element to check", **rKW)

    @commands.group('tasks', hidden=True)
    @commands.is_owner()
    async def signal_tasks(self, ctx):
        """Signal tasks commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help('tasks')

    @signal_tasks.command('start')
    async def start_task(self, ctx, *, task):
        """Start sleeping task"""
        if 'announcements' in task:
            self.get_announcements.start()
        elif 'zoom_parse' in task:
            self.parse_zoom_links.start()
        else:
            return
        await ctx.message.add_reaction(SUCCESS_REACTION)

    @signal_tasks.command('stop')
    async def stop_task(self, ctx, *, task):
        """Stop running task"""
        if 'announcements' in task:
            self.get_announcements.stop()
        elif 'zoom_parse' in task:
            self.parse_zoom_links.stop()
        else:
            return
        await ctx.message.add_reaction(SUCCESS_REACTION)

    @signal_tasks.command('cancel')
    async def cancel_task(self, ctx, *, task):
        """Cancel running task"""
        if 'announcements' in task:
            self.get_announcements.cancel()
        elif 'zoom_parse' in task:
            self.parse_zoom_links.cancel()
        else:
            return
        await ctx.message.add_reaction(SUCCESS_REACTION)

    @start_task.error
    @stop_task.error
    @cancel_task.error
    async def on_signal_tasks_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply('Task name is not specified')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.reply('Task is already in specified state')
        elif isinstance(error, commands.errors.NotOwner):
            await ctx.reply('You are not allowed to use this command')
        else:
            raise error

    @tasks.loop(minutes=10)
    async def get_announcements(self):
        print(log_time() + 'Doing announcements loop')
        last_check = datetime.fromisoformat(open(CANVAS_ANNOUNCEMENTS_FILE_PATH).read())
        announcements = canvas.get_announcements([course.id for course in canvas.get_courses()])
        channel = self.bot.get_channel(CANVAS_ANNOUNCEMENTS_CHANNEL)
        for announcement in announcements:
            if last_check < announcement.posted_at_date:
                course = announcement.get_parent()
                # if announcement  # TODO attachments
                text = markdownify(
                    html=discord.utils.escape_markdown(announcement.message),
                    strip=['img'],
                    heading_style='discord',
                    bullets='•*+'
                )
                text = re.sub(r'(\n\s*){3,}', '\n\n', text)
                text = text.strip()

                embeds = list()
                while text:
                    if len(text) >= EMBED_DESC_MAX_LENGTH:
                        try:
                            break_at = EMBED_DESC_MAX_LENGTH + -text[EMBED_DESC_MAX_LENGTH::-1].index('\n')
                        except ValueError:
                            break_at = EMBED_DESC_MAX_LENGTH

                        embeds.append(discord.Embed(
                            description=text[:break_at].strip()
                        ))

                        text = text[break_at:]
                    else:
                        embeds.append(discord.Embed(
                            description=text
                        ))

                        break

                embeds[0].title = announcement.title
                embeds[0].url = announcement.url

                author = announcement.author
                embeds[0].set_author(
                    name=author["display_name"],
                    url=author["html_url"],
                    icon_url=author["avatar_image_url"]
                )

                embeds[-1].timestamp = announcement.posted_at_date
                embeds[-1].set_footer(text=course.name)

                for embed in embeds:
                    embed.colour = to_colour(course.id)

                for embed in embeds:
                    await channel.send(embed=embed)

                if self.last_post:
                    if self.last_post < announcement.posted_at_date:
                        self.last_post = announcement.posted_at_date
                else:
                    self.last_post = announcement.posted_at_date

        if self.last_post:
            open(CANVAS_ANNOUNCEMENTS_FILE_PATH, 'w').write(self.last_post.isoformat())

    @tasks.loop(hours=1)
    async def parse_zoom_links(self):
        meetings = list()

        print(log_time() + 'Running Zoom parsing loop')
        if 0 < datetime.now().hour < 6:
            print('\tTime-based return')
            return

        course = canvas.get_course(7856)
        for module in course.get_modules():
            if 'week ' in module.name:
                for item in module.get_module_items():
                    if 'week ' in item.title and item.type == 'Page':
                        week_num = int(re.search(r'\d', item.title)[0])
                        page = course.get_page(item.page_url)
                        soup = BeautifulSoup(page.body, 'html.parser')
                        start_time = password = None

                        for link in soup.find_all('a'):
                            if link.find(text=re.compile('utwente-nl.zoom.us/j/')):
                                count = 0
                                for element in link.previousGenerator():
                                    if element != '\n':
                                        if element.name == 'li' and '<strong' in str(element):
                                            start_time = int(re.search(r'\d', element.text)[0])
                                            start_time = HOURS[start_time][0]
                                            weekday = re.search(r'(Mo(n(day)?)?|Tu(e(sday)?)?|We(d(nesday)?)?|Th(u(rsday)?)?|Fr(i(day)?)?|Sa(t(urday)?)?|Su(n(day)?)?)', element.text)[0]
                                            start_time = datetime.fromisocalendar(2021, 4 + 1 + week_num, tstrptime(weekday, '%A').tm_wday + 1).replace(hour=start_time.hour, minute=start_time.minute)
                                            break  # because week 3 -> week 4
                                        count += 1
                                    if count > 15:
                                        break
                                count = 0
                                for element in link.nextGenerator():
                                    if element != '\n':
                                        if isinstance(element, bs4.element.Tag) and re.search(r'[Pp][Aa][Ss][Ss].+\d{6}', element.text):
                                            password = re.search(r'\d{6}', element.text)[0]
                                            break
                                        count += 1
                                    if count > 10:
                                        break
                                meetings.append({
                                    'link': link.get('href'),
                                    'start_time': start_time,
                                    'password': password
                                })

        append_meetings(meetings)
        await self.schedule_meetings()
        print(log_time() + '\tZoom loop ended')

    @get_announcements.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Loop(bot))
