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
"""Discord extension for managing server roles."""
import functools
import typing

import discord
from discord.ext import commands

from ..utils.persistent_settings import DiscordIDSettings

guild_settings = DiscordIDSettings("roles")

ROLES_MESSAGE_DELETE_DELAY = 60


def delete_command_message(delay=10, only_on_success=False):
    """Return command decorator that deletes the command message."""

    def decorator(command):
        @functools.wraps(command)
        async def wrapper(self, ctx, *args, **kwargs):
            ret = await command(self, ctx, *args, **kwargs)
            if not only_on_success or ret:
                await ctx.message.delete(delay=delay)
            return ret

        return wrapper

    return decorator


class Roles(commands.Cog, name="Server Roles"):
    """Manage server roles."""

    def __init__(self, bot):
        """Initialize cog for managing roles."""
        self.bot = bot

    @commands.command(
        name="role",
        aliases=["roles"],
        brief="Self-assign a role",
        usage="<role> | <role-key>",
    )
    @commands.guild_only()
    @delete_command_message()
    async def role(self, ctx, *, role: typing.Union[discord.Role, str]):
        """Self-assign a given role, toggling between adding and removing."""
        public_roles = guild_settings.get(ctx.bot, ctx.guild.id, "public_roles", {})
        if isinstance(role, discord.Role):
            roles_by_id = {r["id"]: r for k, r in public_roles.items()}
            # switch public_roles over to a dict with the role id as the key
            public_roles = roles_by_id
            role_key = role.id
        else:
            role_str = role.lower()
            if not role_str or role_str == "list":
                lines = ["I'm aware of the following roles:", ""]
                lines += [
                    # "`{0}`: <@&{1}> -- {2}".format(k, r["id"], r["description"])
                    "`{0}`: {1} -- {2}".format(k, r["name"], r["description"])
                    for k, r in sorted(public_roles.items())
                ]
                await ctx.send(
                    "\n".join(lines),
                    delete_after=ROLES_MESSAGE_DELETE_DELAY,
                    # allowed_mentions=discord.AllowedMentions(
                    #     everyone=False, users=False, roles=False
                    # ),
                )
                return
            role_key = role_str
        try:
            role_dict = public_roles[role_key]
        except KeyError:
            missingstr = (
                f"I can't find that role. Try `{ctx.prefix}{ctx.command} list` for a"
                f" list of self-assignable roles."
            )
            await ctx.send(missingstr, delete_after=ROLES_MESSAGE_DELETE_DELAY)
            return
        member = ctx.message.author
        discord_role = ctx.guild.get_role(role_dict["id"])
        if discord_role in member.roles:
            await member.remove_roles(discord_role)
        else:
            await member.add_roles(discord_role)

    @commands.command(brief="Add a public role", usage="<role> <key> <description>")
    @commands.has_permissions(manage_roles=True)
    @delete_command_message()
    async def addpublicrole(
        self, ctx, role: discord.Role, key: str, *, description: str
    ):
        """Make an existing role self-assignable through the role command."""
        role_dict = dict(id=role.id, name=role.name, description=description)
        public_roles = guild_settings.get(ctx.bot, ctx.guild.id, "public_roles")
        if public_roles is None:
            public_roles = {}
        public_roles[key] = role_dict
        guild_settings.set(ctx.bot, ctx.guild.id, "public_roles", public_roles)

    @commands.command(brief="Remove a public role", usage="<role>")
    @commands.has_permissions(manage_roles=True)
    @delete_command_message()
    async def removepublicrole(self, ctx, *, role: discord.Role):
        """Make a role no longer self-assignable through the role command."""
        public_roles = guild_settings.get(ctx.bot, ctx.guild.id, "public_roles")
        if public_roles is None:
            public_roles = {}
        for _key, role_dict in public_roles.items():
            if role_dict["id"] == role.id:
                break
        else:
            missingstr = f"{role.name} is not in the list of self-assignable roles."
            await ctx.send(missingstr, delete_after=ROLES_MESSAGE_DELETE_DELAY)
            return
        public_roles.pop(_key)
        guild_settings.set(ctx.bot, ctx.guild.id, "public_roles", public_roles)


def setup(bot):
    """Set up the roles extension."""
    # set up persistent roles guild settings
    guild_settings.setup(bot)

    bot.add_cog(Roles(bot))


def teardown(bot):
    """Tear down the roles extension."""
    # tear down persistent roles guild settings
    guild_settings.teardown(bot)
