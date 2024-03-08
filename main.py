'''
Core of Economy System

Copyright (C) 2024  __OopsYouDiedE__

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import sqlite3
import interactions
from interactions.api.events import MemberRemove, MessageCreate
from interactions.ext.paginators import Paginator
from collections import deque
import asyncio
import datetime
from config import DEV_GUILD
from typing import Optional, Union
import tempfile
import os
import asyncio
import csv

import aiofiles
import aiofiles.ospath
import aiofiles.os
import aioshutil
from aiocsv import AsyncReader, AsyncDictReader, AsyncWriter, AsyncDictWriter
from . import database_manager


class CoreEconomySystem(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="core",
        description="Minimize Core For Economy Simulation"
    )

    # 管理员指令：添加指定数量的物品给某人。
    @module_base.subcommand("give", sub_cmd_description="直接在某人账户中添加特定数量物品。这是作弊行为。")
    @interactions.check(interactions.is_owner())
    @interactions.slash_option(
        name="user_id",
        description="接收人",
        required=True,
        opt_type=interactions.OptionType.USER
    )
    @interactions.slash_option(
        name="object_name",
        description="物品名称",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    @interactions.slash_option(
        name="quantity",
        description="添加数量",
        required=True,
        opt_type=interactions.OptionType.NUMBER,
    )
    async def command_give_item(self, ctx: interactions.SlashContext, user_id: str, object_name: str,
                                quantity: int = 1):
        await ctx.send(f"DEBUG:交易前{user_id},有{database_manager.query_item(user_id, object_name)}个{object_name}")
        database_manager.update_item(user_id, object_name, quantity)

        await ctx.send(f"DEBUG:将{object_name}*{quantity}给予{user_id}")
        await ctx.send(f"DEBUG:交易后{user_id},有{database_manager.query_item(user_id, object_name)[2]}个{object_name}")

    # 普通人指令：将自己的物品无条件赠送给另一个人呢
    @module_base.subcommand("send",
                            sub_cmd_description="将自己的一件物品发送给另一个人。")
    @interactions.slash_option(
        name="receiver_id",
        description="接收者",
        required=True,
        opt_type=interactions.OptionType.USER
    )
    @interactions.slash_option(
        name="object_name",
        description="物品名称",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    @interactions.slash_option(
        name="quantity",
        description="发送物品数量",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    async def command_send_item(self, ctx: interactions.SlashContext, receiver_id: str,
                                object_name: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send(f"禁止交易数量小于1")
            return

        sender_id = ctx.user
        info = database_manager.query_item(sender_id, object_name)
        if info[2] - quantity < 0:
            await ctx.send(f"您有{info[2]}个物品，您要发送{quantity}。数量不够，无法交易。")
            return
        database_manager.update_item(sender_id, object_name, -quantity)
        database_manager.update_item(receiver_id, object_name, quantity)
        await ctx.send(f"交易成功！您赠送给{receiver_id} {quantity}个 {object_name}")

        # 普通人指令：查看自己全部物品数量

    @module_base.subcommand("show_item",
                            sub_cmd_description="显示自己某件物品或全部物品数量。")
    @interactions.slash_option(
        name="item",
        description="查看的特定物品，不填则为查看全部物品。",
        required=False,
        opt_type=interactions.OptionType.STRING
    )
    async def command_check_item(self, ctx: interactions.SlashContext, item: str = ''):
        if item == '':
            await ctx.send(database_manager.get_items_by_uid(str(ctx.user)))
        else:
            await ctx.send(str(database_manager.query_item(str(ctx.user))))

    @module_base.subcommand("del_all", sub_cmd_description="删除全部数据，慎用！")
    @interactions.check(interactions.is_owner())
    @interactions.slash_option(
        name="key",
        description="在该命令处KEY",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def del_all(self, ctx: interactions.SlashContext, key: str):
        if key == '%DEL_ALL': database_manager.delete_all_data()
        await ctx.send('您销毁了全部数据库。')

    @module_base.subcommand("get_all_data", sub_cmd_description="获取所有人和物品记录。")
    @interactions.check(interactions.is_owner())
    async def del_all(self, ctx: interactions.SlashContext):
        await ctx.send(database_manager.get_all_records())
