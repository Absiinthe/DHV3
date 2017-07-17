# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

import time

import discord
from discord.ext import commands
from prettytable import PrettyTable

from cogs.utils import comm, commons, ducks, prefs, scores
from cogs.utils.commons import _
from .utils import checks


class ServerAdmin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def coin(self, ctx):
        """Spawn a duck on the current channel
        !coin"""
        from cogs.utils.ducks import spawn_duck
        await spawn_duck({
            "channel": ctx.message.channel,
            "time"   : int(time.time())
        })

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def game_ban(self, ctx, member: discord.Member):
        """Ban someone from the bot on the current channel
        !game_ban [member]"""
        language = prefs.getPref(ctx.message.guild, "language")

        scores.setStat(ctx.message.channel, member, "banned", True)
        await comm.message_user(ctx.message, _(":ok: Done, user banned :gun:", language))

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def game_unban(self, ctx, member: discord.Member):
        """Unban someone from the bot on the current channel
        !game_unban [member]"""
        language = prefs.getPref(ctx.message.guild, "language")

        scores.setStat(ctx.message.channel, member, "banned", False)
        await comm.message_user(ctx.message, _(":ok: Done, user unbanned :eyes:", language))

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def give_exp(self, ctx, target: discord.Member, exp: int):
        """Give exp to a player.
        Require admin powers
        !give_exp [target] [exp]"""
        try:
            scores.addToStat(ctx.message.channel, target, "exp", exp)
        except OverflowError:
            await comm.message_user(ctx.message, _("Congratulations, you sent / gave more experience than the maximum number I'm able to store.", prefs.getPref(ctx.message.guild, "language")))
            return
        await comm.logwithinfos_ctx(ctx, "[giveexp] Giving " + str(exp) + " exp points to " + target.mention)
        await comm.message_user(ctx.message, _(":ok:, they now have {newexp} exp points !", prefs.getPref(ctx.message.guild, "language")).format(**{
            "newexp": scores.getStat(ctx.message.channel, target, "exp")
        }))

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def add_channel(self, ctx):
        """Add the current channel to the server
        !add_channel
        """
        language = prefs.getPref(ctx.message.guild, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        if not "channels" in servers[ctx.message.guild.id]:
            servers[ctx.message.guild.id]["channels"] = []

        if not ctx.message.channel.id in servers[ctx.message.guild.id]["channels"]:
            await comm.logwithinfos_ctx(ctx, "Adding channel {name} | {id} to channels.json...".format(**{
                "id"  : ctx.message.channel.id,
                "name": ctx.message.channel.name
            }))
            servers[ctx.message.guild.id]["channels"] += [ctx.message.channel.id]
            prefs.JSONsaveToDisk(servers, "channels.json")
            await ducks.planifie(ctx.message.channel)
            await comm.message_user(ctx.message, _(":robot: Channel added !", language))

        else:
            await comm.logwithinfos_ctx(ctx, "Channel exists")
            await comm.message_user(ctx.message, _(":x: This channel already exists in the game.", language))

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def del_channel(self, ctx):
        """!del_channel
        Remove the current channel from the server
        """
        await ducks.del_channel(ctx.message.channel)
        await comm.message_user(ctx.message, _(":ok: Channel deleted", prefs.getPref(ctx.message.guild, "language")))

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def duckplanning(self, ctx):
        """!duckplanning
        DEPRECATED ! Get the number of ducks left to spawn on the channel
        """
        await comm.message_user(ctx.message, _("There is {ducks} ducks left to spawn today !", prefs.getPref(ctx.message.guild, "language")).format(ducks=commons.ducks_planned[ctx.message.channel]))

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def add_admin(self, ctx, target: discord.Member):
        """!add_admin [target]
        Remove an admin to the server
        """
        language = prefs.getPref(ctx.message.guild, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        servers[ctx.message.guild.id]["admins"] += [target.id]
        await comm.logwithinfos_ctx(ctx, "Adding admin {admin_name} | {admin_id} to configuration file for server {server_name} | {server_id}.".format(**{
            "admin_name" : target.name,
            "admin_id"   : target.id,
            "server_name": ctx.message.guild.name,
            "server_id"  : ctx.message.guild.id
        }))
        await comm.message_user(ctx.message, _(":robot: OK, {name} was set as an admin on the server !", language).format(**{
            "name": target.name
        }))

        prefs.JSONsaveToDisk(servers, "channels.json")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def del_admin(self, ctx, target: discord.Member):
        """!del_admin [target]
        Remove an admin from the server
        """
        language = prefs.getPref(ctx.message.guild, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        if target.id in servers[ctx.message.guild.id]["admins"]:
            servers[ctx.message.guild.id]["admins"].remove(target.id)
            await comm.logwithinfos_ctx(ctx, "Deleting admin {admin_name} | {admin_id} from configuration file for server {server_name} | {server_id}.".format(**{
                "admin_name" : target.name,
                "admin_id"   : target.id,
                "server_name": ctx.message.guild.name,
                "server_id"  : ctx.message.guild.id
            }))
            await comm.message_user(ctx.message, _(":robot: OK, {name} was removed from this server admins !", language).format(**{
                "name": target.name
            }))

            prefs.JSONsaveToDisk(servers, "channels.json")


        else:
            await comm.message_user(ctx.message, _(":robot: OK, {name} is not an admin !", language).format(**{
                "name": target.name
            }))

    @commands.command(pass_context=True)
    async def claimserver(self, ctx):
        """Sets yourself as an admin if there are no admin configured, IE: when you just added the bot to a server
        !claimserver"""
        language = prefs.getPref(ctx.message.guild, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        if not str(ctx.message.guild.id) in servers:
            servers[str(ctx.message.guild.id)] = {}
        if not "admins" in servers[str(ctx.message.guild.id)] or not servers[str(ctx.message.guild.id)]["admins"]:
            servers[str(ctx.message.guild.id)]["admins"] = [str(ctx.message.author.id)]
            await comm.logwithinfos_ctx(ctx, "Adding admin {admin_name} | {admin_id} to configuration file for server {server_name} | {server_id}.".format(**{
                "admin_name" : ctx.message.author.name,
                "admin_id"   : ctx.message.author.id,
                "server_name": ctx.message.guild.name,
                "server_id"  : ctx.message.guild.id
            }))
            await comm.message_user(ctx.message, _(":robot: OK, you have been set as an admin !", language))
        else:
            await comm.logwithinfos_ctx(ctx, "An admin already exist")
            await comm.message_user(ctx.message, _(":x: An admin exist on this server ! Try !add_admin", language))
        prefs.JSONsaveToDisk(servers, "channels.json")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def permissions(self, ctx):
        """Check permissions given to the bot. You'll need admin powers
        !permissions"""
        permissionsToHave = ["change_nicknames", "connect", "create_instant_invite", "embed_links", "manage_messages", "mention_everyone", "read_messages", "send_messages", "send_tts_messages"]
        permissions_str = ""
        for permission, value in ctx.message.guild.me.permissions_in(ctx.message.channel):
            if value:
                emo = ":white_check_mark:"
            else:
                emo = ":negative_squared_cross_mark:"
            if (value and permission in permissionsToHave) or (not value and not permission in permissionsToHave):
                pass
            else:
                emo += ":warning:"
            permissions_str += "\n{value}\t{name}".format(**{
                "value": emo,
                "name" : str(permission)
            })
        await comm.message_user(ctx.message, _("Permissions : {permissions}", prefs.getPref(ctx.message.guild, "language")).format(**{
            "permissions": permissions_str
        }))

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_admin()
    async def deleteeverysinglescoreandstatonthischannel(self, ctx):
        """Delete scores and stats of players on this channel. You'll need admin powers
        !deleteeverysinglescoreandstatonthischannel"""
        scores.delChannelPlayers(ctx.message.channel)
        await comm.message_user(ctx.message, _(":ok: Scores / stats of the channel were succesfully deleted.", prefs.getPref(ctx.message.guild, "language")))

    ### SETTINGS ###

    @commands.group(pass_context=True)
    @checks.is_activated_here()
    async def settings(self, ctx):
        language = prefs.getPref(ctx.message.guild, "language")

        if not ctx.invoked_subcommand:
            await comm.message_user(ctx.message, _(":x: Incorrect syntax : `!settings [view/set/reset/list/modified] [setting if applicable]`", language))

    @settings.command(pass_context=True, name="view")
    async def view(self, ctx, pref: str):
        """!settings view [pref]"""
        language = prefs.getPref(ctx.message.guild, "language")

        if pref in commons.defaultSettings.keys():
            await comm.message_user(ctx.message, _("The setting {pref} is set at {value} on this server.", language).format(**{
                "value": prefs.getPref(ctx.message.guild, pref),
                "pref" : pref
            }))
        else:
            await comm.message_user(ctx.message, _(":x: Invalid preference, maybe a typo ? Check the list with `!settings list`", language))

    @settings.command(pass_context=True, name="set")
    @checks.is_admin()
    async def set(self, ctx, pref: str, value: str):
        """!settings set [pref] [value]
        Admin powers required"""
        language = prefs.getPref(ctx.message.guild, "language")

        if pref in commons.defaultSettings.keys():
            try:
                if pref == "ducks_per_day":
                    maxCJ = int(125 + (ctx.message.guild.member_count / (5 + (ctx.message.guild.member_count / 300))))
                    if int(value) > maxCJ:
                        if ctx.message.author.id in commons.owners:
                            await comm.message_user(ctx.message, _("Bypassing the max_ducks_per_day check as you are the bot owner. It would be {max}", language).format(**{
                                "max": maxCJ
                            }))
                        else:
                            value = maxCJ
            except TypeError:
                await comm.message_user(ctx.message, _(":x: Incorrect value", language))
                return

            except ValueError:
                await comm.message_user(ctx.message, _(":x: Incorrect value", language))
                return

            if prefs.setPref(ctx.message.guild, pref=pref, value=value):
                if pref == "ducks_per_day":
                    await ducks.planifie(ctx.message.channel)
                await comm.message_user(ctx.message, _(":ok: The setting {pref} was set at `{value}` on this server.", language).format(**{
                    "value": prefs.getPref(ctx.message.guild, pref),
                    "pref" : pref
                }))
            else:
                await comm.message_user(ctx.message, _(":x: Incorrect value", language))
        else:
            await comm.message_user(ctx.message, _(":x: Invalid preference, maybe a typo ? Check the list with `!settings list`", language))

    @settings.command(pass_context=True, name="reset")
    @checks.is_admin()
    async def reset(self, ctx, pref: str):
        """!settings reset [pref]
        Admin powers required"""
        language = prefs.getPref(ctx.message.guild, "language")

        if pref in commons.defaultSettings.keys():
            prefs.setPref(ctx.message.guild, pref)
            await comm.message_user(ctx.message, _(":ok: The setting {pref} reset to it's defalut value on this server : `{value}` ", language).format(**{
                "value": prefs.getPref(ctx.message.guild, pref),
                "pref" : pref
            }))
        else:
            await comm.message_user(ctx.message, _(":x: Invalid preference, maybe a typo ? Check the list with `!settings list`", language))

    @settings.command(pass_context=True, name="list")
    async def list(self, ctx):
        """!settings list"""
        language = prefs.getPref(ctx.message.guild, "language")

        await comm.message_user(ctx.message, _("List of preferences is available on the new website : https://api-d.com/bot-settings.html", language))

    @settings.command(pass_context=True, name="modified")
    async def listm(self, ctx):
        """!settings modified"""
        language = prefs.getPref(ctx.message.guild, "language")
        defaultSettings = commons.defaultSettings
        x = PrettyTable()

        x._set_field_names([_("Parameter", language), _("Value", language), _("Default value", language)])
        for param in defaultSettings.keys():
            if prefs.getPref(ctx.message.guild, param) != defaultSettings[param]["value"]:
                x.add_row([param, prefs.getPref(ctx.message.guild, param), defaultSettings[param]["value"]])

        await comm.message_user(ctx.message, _("List of modified parameters : \n```{table}```", language).format(**{
            "table": x.get_string(sortby=_("Parameter", language))
        }))


def setup(bot):
    bot.add_cog(ServerAdmin(bot))
