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
    async def prepare_help_command(self, ctx, command):
        """Customized to delete command message."""
        delete_delay = 30
        if ctx.guild is not None:
            # command is in a text channel, delete response after some time
            await ctx.send("I've sent you a Direct Message.", delete_after=delete_delay)
            await ctx.message.delete(delay=delete_delay)
        await super().prepare_help_command(ctx, command)


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
    help_command=CustomHelpCommand(sort_commands=False, dm_help=True),
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
