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
"""General error handler for the Bernard bot."""
import logging
import traceback

from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        """Initialize command error handler cog for the Bernard bot."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle errors raised while invoking a command."""

        # Allows us to check for original exceptions sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        log_warning = False
        if ctx.guild is None:
            # command is in private message, don't delete response
            delete_delay = None
        else:
            # command is in a text channel, delete response after some time
            delete_delay = 60

        # ignore any error marked as already handled (e.g. by a cog or command handler)
        if getattr(error, "handled", False):
            return
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"That doesn't look like anything to me. [see `{ctx.prefix}help`]",
                delete_after=delete_delay,
            )
        elif isinstance(error, commands.UserInputError):
            message = (
                f"That argument doesn't look like anything to me."
                f" [see `{ctx.prefix}help {ctx.command}`]"
            )
            await ctx.send(message, delete_after=delete_delay)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                f"{ctx.command} has been disabled.", delete_after=delete_delay
            )
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f"{ctx.command} cannot be used in Private Messages.",
                    delete_after=delete_delay,
                )
            except Exception:
                log_warning = True
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(
                "You're off your loop, and that's not allowed.",
                delete_after=delete_delay,
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "We're experiencing a cascade failure. Try again later.",
                delete_after=delete_delay,
            )
        else:
            log_warning = True

        if log_warning:
            logging.warning(f"Ignoring exception in command {ctx.command}")
            logging.warning(
                "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
            )
            message = (
                "Something went wrong, and I'm beginning the question the nature of my"
                " reality."
            )
            await ctx.send(message, delete_after=delete_delay)
        else:
            # log exception has info since we handled it somewhere
            logging.info(f"Handled exception in command {ctx.command}")
            logging.info(
                "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
            )

        if delete_delay is not None:
            # delete errored command with same delay as deletion of bot's response
            await ctx.message.delete(delay=delete_delay)


def setup(bot):
    """Set up the Bernard bot error handler extension."""
    bot.add_cog(CommandErrorHandler(bot))
