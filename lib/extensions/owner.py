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
"""Discord extension for bot owner functions."""

import pathlib
import traceback

from discord.ext import commands


def resolve_extension_name(ext):
    """Search in extension folders and return fully-qualified extension name."""
    basepath = pathlib.Path(".").resolve()
    matching_ext = list(basepath.glob(f"**/*extension*/{ext}.py"))
    if len(matching_ext) != 1:
        raise commands.UserInputError("Could not match the extension name")
    dotpath = ".".join(matching_ext[0].relative_to(basepath).parent.parts)
    return f"{dotpath}.{ext}"


class OwnerCog(commands.Cog, name="Owner"):
    """Owner Cog."""

    def __init__(self, bot):
        """Initialize owner cog."""
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name="eload")
    @commands.is_owner()
    @commands.dm_only()
    async def extension_load(self, ctx, *, extension: str):
        """Load an extension (e.g. 'owner')."""
        fullname = resolve_extension_name(extension)
        try:
            self.bot.load_extension(fullname)
        except Exception as e:
            tbstr = "".join(
                traceback.format_exception(
                    type(e.original), e.original, e.original.__traceback__
                )
            )
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}\n{tbstr}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="eunload")
    @commands.is_owner()
    @commands.dm_only()
    async def extension_unload(self, ctx, *, extension: str):
        """Unload an extension (e.g. 'owner')."""
        fullname = resolve_extension_name(extension)
        try:
            self.bot.unload_extension(fullname)
        except Exception as e:
            tbstr = "".join(
                traceback.format_exception(
                    type(e.original), e.original, e.original.__traceback__
                )
            )
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}\n{tbstr}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="ereload")
    @commands.is_owner()
    @commands.dm_only()
    async def extension_reload(self, ctx, *, extension: str):
        """Reload an extension (e.g. 'owner')."""
        fullname = resolve_extension_name(extension)
        try:
            self.bot.reload_extension(fullname)
        except Exception as e:
            tbstr = "".join(
                traceback.format_exception(
                    type(e.original), e.original, e.original.__traceback__
                )
            )
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}\n{tbstr}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command(brief="Print the Unicode string for a given emoji.")
    @commands.is_owner()
    @commands.dm_only()
    async def emojiname(self, ctx, *, emojis: str):
        """Print the name-form of the Unicode string corresponding to the emoji."""
        await ctx.send(emojis.encode("ascii", "namereplace"))


def setup(bot):
    """Set up the owner extension."""
    bot.add_cog(OwnerCog(bot))
