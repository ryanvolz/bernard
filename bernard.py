# ----------------------------------------------------------------------------
# Copyright (c) 2020 Ryan Volz
# All rights reserved.
#
# Distributed under the terms of the BSD 3-clause license.
#
# The full license is in the LICENSE file, distributed with this software.
#
# SPDX-License-Identifier: BSD-3-Clause
# ----------------------------------------------------------------------------
"""Bernard - Discord bot and Head of Behavior."""

import itertools
import logging
import os

import discord
from discord.ext import commands

logging.basicConfig(level=logging.WARNING)

bot_token = os.getenv("DISCORD_TOKEN")
owner_id = os.getenv("DISCORD_OWNER")
if owner_id is not None:
    owner_id = int(owner_id)


class CustomHelpCommand(commands.DefaultHelpCommand):
    delete_delay = 30

    async def prepare_help_command(self, ctx, command):
        """Customized to delete command message."""
        if ctx.guild is not None:
            # command is in a text channel, delete response after some time
            await ctx.message.delete(delay=self.delete_delay)
        await super().prepare_help_command(ctx, command)

    async def send_error_message(self, error):
        """Always send error message to the command context"""
        await self.context.send(error, delete_after=self.delete_delay)

    async def send_pages(self):
        """Notify user in channel if the response is coming as a DM."""
        destination = self.get_destination()
        dest_type = getattr(destination, "type", None)
        if self.context.guild is not None and dest_type != discord.ChannelType.text:
            await self.context.send(
                "I've sent you a Direct Message.", delete_after=self.delete_delay
            )
        for page in self.paginator.pages:
            await destination.send(page)

    # override send_bot_help with fix so that unsorted commands stay in right order
    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            # <description> portion
            self.paginator.add_line(bot.description, empty=True)

        no_category = "\u200b{0.no_category}:".format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ":" if cog is not None else no_category

        filtered = []
        for _cogname, cog in sorted(bot.cogs.items()):
            # hard-code no sorting here so that commands are displayed in the order
            # that they are defined, but allow sort_commands to be used at other levels
            cog_filtered = await self.filter_commands(cog.get_commands(), sort=False)
            filtered.extend(cog_filtered)
        max_size = self.get_max_size(filtered)
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, cmds in to_iterate:
            self.add_indented_commands(list(cmds), heading=category, max_size=max_size)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()


def get_prefix(bot, message):
    """Customize prefix by using a callable."""
    prefixes = ["! ", "!", ". ", "."]

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        return prefixes + ["? ", "?"]

    # If we are in a guild, we allow for the user to mention us or use any of the
    # prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = [
    "lib.botc_extensions.townsquare",
    "lib.botc_extensions_private.characters",
    "lib.extensions.bernard_error_handler",
    "lib.extensions.owner",
    "lib.extensions.roles",
]

bot = commands.Bot(
    command_prefix=get_prefix,
    description="Bernard - Discord bot and Head of Behavior",
    help_command=CustomHelpCommand(
        sort_commands=True, dm_help=None, dm_help_threshold=160
    ),
    owner_id=owner_id,
)

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)

    @bot.event
    async def on_ready():
        """Print status message when ready."""
        status = (
            f"\n\nLogged in as: {bot.user.name} - {bot.user.id}"
            f"\nVersion: {discord.__version__}\n"
        )
        print(status)

    bot.run(bot_token, bot=True, reconnect=True)
