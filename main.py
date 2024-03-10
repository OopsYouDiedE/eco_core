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
import os
import random

import interactions
from . import database_manager
from .utils import IDManager,KeyValueManager
'''
The DEV_GUILD must be set to a specific guild_id
'''


async def administer_or_allowed_id(ctx: interactions.BaseContext):
    res: bool = await interactions.is_owner()(ctx)
    if os.environ.get("ROLE_ID"):
        if ctx.author.has_role(os.environ.get("ROLE_ID")): return True
    else:
        if ctx.author.guild_permissions.ADMINISTRATOR: return True
        if ctx.author.has_role(*tuple(id_manager.load_ids())): return True
    return False


id_manager = IDManager(f'{os.path.dirname(__file__)}/ids.txt')
exchangeable_item = IDManager(f'{os.path.dirname(__file__)}/exchangeable_item.txt')
coin_and_owner = KeyValueManager(f'{os.path.dirname(__file__)}/coin_and_owner.yaml')
market_manager = KeyValueManager(f'{os.path.dirname(__file__)}/market_manager.yaml')
exchangeable_item.add_id('劳动券')


class Core(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="core",
        description="Minimize Core For Economy Simulation"
    )

    # 管理员指令：添加指定数量的物品给某人。
    @module_base.subcommand("give", sub_cmd_description="直接在某人账户中添加特定数量物品。这是作弊行为。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="user_id",
        description="接收人",
        required=True,
        opt_type=interactions.OptionType.USER
    )
    @interactions.slash_option(
        name="item",
        description="物品名",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    @interactions.slash_option(
        name="quantity",
        description="添加数量",
        required=True,
        opt_type=interactions.OptionType.NUMBER,
    )
    async def command_give_item(self, ctx: interactions.SlashContext, user_id: str, item: str,
                                quantity: int):
        await ctx.send(f"DEBUG:交易前{user_id},有{database_manager.query_item(user_id, item)}个{item}")
        database_manager.update_item(user_id, item, quantity)

        await ctx.send(f"DEBUG:将{item}*{quantity}给予{user_id}")
        await ctx.send(f"DEBUG:交易后{user_id},有{database_manager.query_item(user_id, item)[2]}个{item}")

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
        name="item",
        description="发送物品",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=False
    )
    @interactions.slash_option(
        name="quantity",
        description="发送物品数量",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    async def command_send_item(self, ctx: interactions.SlashContext, receiver_id: str,
                                item: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send(f"禁止交易数量小于1")
            return

        sender_id = ctx.user
        info = database_manager.query_item(sender_id, item)
        if info[2] - quantity < 0:
            await ctx.send(f"您有{info[2]}个物品，您要发送{quantity}。数量不够，无法交易。")
            return
        database_manager.update_item(sender_id, item, -quantity)
        database_manager.update_item(receiver_id, item, quantity)
        await ctx.send(f"交易成功！您赠送给{receiver_id} {quantity}个 {item}")

        # 普通人指令：查看自己全部物品数量

    @module_base.subcommand("show_item",
                            sub_cmd_description="显示自己某件物品或全部物品数量。")
    @interactions.slash_option(
        name="items",
        description="查看的特定物品，不填则为查看全部物品。",
        required=False,
        opt_type=interactions.OptionType.STRING,
        autocomplete=False
    )
    async def command_check_item(self, ctx: interactions.SlashContext, items: str = ''):
        if items == '':
            await ctx.send(database_manager.get_items_by_uid(str(ctx.user)))
        else:
            await ctx.send(str(database_manager.query_item(str(ctx.user), items)))

    @module_base.subcommand("del_all", sub_cmd_description="删除全部数据，慎用！")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="key",
        description="在该命令处KEY",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def del_all(self, ctx: interactions.SlashContext, key: str):
        if key == '%DEL_ALL':
            database_manager.delete_all_data()
            await ctx.send('您销毁了全部数据库。')
        else:
            await ctx.send('key错误。这个key在该代码执行处查看。')

    @module_base.subcommand("get_all_data", sub_cmd_description="获取所有人和物品记录。")
    @interactions.check(administer_or_allowed_id)
    async def get_all(self, ctx: interactions.SlashContext):
        await ctx.send(database_manager.get_all_records())

    @module_base.subcommand("add_role", sub_cmd_description="添加管理员身份组。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="role_id",
        description="身份组",
        required=True,
        opt_type=interactions.OptionType.ROLE
    )
    async def add_role(self, ctx: interactions.SlashContext, role_id: interactions.Role):
        await ctx.send(id_manager.add_id('@' + str(role_id.id)))

    @module_base.subcommand("del_role", sub_cmd_description="删除管理员身份组。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="role_id",
        description="身份组",
        required=True,
        opt_type=interactions.OptionType.ROLE
    )
    async def del_role(self, ctx: interactions.SlashContext, role_id: interactions.Role):
        await ctx.send(id_manager.remove_id('@' + str(role_id.id)))


"""class Market(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="market",
        description="实时在线买卖您的商品！"
    )

    # 交易流程：每个人可以发送一个订单，这个订单是交易唯一凭证
    @module_base.subcommand("sell", sub_cmd_description="卖出您的商品！。")
    @interactions.slash_option(
        name="item",
        description="产品名称",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=False
    )
    @interactions.slash_option(
        name="num",
        description="数量",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    @interactions.slash_option(
        name="exchange_item",
        description="交换产品",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=False
    )
    @interactions.slash_option(
        name="exchange_num",
        description="数量",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    @interactions.slash_option(
        name="max_count",
        description="该单全部成交单量",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    async def sell_item(self, ctx: interactions.SlashContext, item: str, num: int, exchange_item: str,
                        exchange_num: int):
        ret_id = market_manager.add_kv()
        await ctx.send(f"您已经提交订单，销售{item}*{num}，交换物品为{exchange_item}*{exchange_num}，销售id为\n{ret_id}")

    # 普通人指令：买产品。
    @module_base.subcommand("buy",
                            sub_cmd_description="输入id号，买物品。")
    @interactions.slash_option(
        name="sell_id",
        description="售单id",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def buy_item(self, ctx: interactions.SlashContext, sell_id: str):
        await ctx.send(f"{market_manager.buy(ctx.user, sell_id)}")"""


class Work(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="work",
        description="签到了，点赞了！"
    )

    # 所有人指令：卖你的产品！
    @module_base.subcommand("check_in", sub_cmd_description="获得你的点赞和劳动券！")
    @interactions.cooldown(interactions.Buckets.USER, 1, 15 * 60 * 60)
    async def check_in(self, ctx: interactions.SlashContext):
        database_manager.update_item(ctx.user, '劳动券', 3)
        database_manager.update_item(ctx.user, '点赞', 3)
        await ctx.send(f"您获得劳动券和点赞！")

    # 检查冷却时间
    # Error handling for the cooldown
    # 普通人指令：买产品。
    @module_base.subcommand("like",
                            sub_cmd_description="给你喜欢的人一个赞。")
    @interactions.slash_option(
        name="user_id",
        description="给他点赞",
        required=True,
        opt_type=interactions.OptionType.USER
    )
    async def like_sb(self, ctx: interactions.SlashContext, user_id: interactions.User):
        database_manager.update_item(ctx.user, '劳动券', 3)
        info = database_manager.query_item(ctx.user, '点赞')
        if info[2] - 1 < 0:
            await ctx.send(f"您没有点赞。通过签到获得。")
            return
        else:
            database_manager.update_item(ctx.user, '点赞', -1)
            database_manager.update_item(user_id, '赞许', 1)
            await ctx.send(f"{user_id}收获了您的赞许！")


class Banknotes(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="banknotes",
        description="满足各位发行货币的需求,只要你有一台印钞机！"
    )

    # 所有人指令：有印钞机的，尽情发行你的货币吧！
    @module_base.subcommand("set_money_printing",
                            sub_cmd_description="设定你专属发行纸币！")
    @interactions.slash_option(
        name="coin_name",
        description="为你的金币取名！取名规则为某某币，如果名字里没有币，或者coin是不行的！",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    @interactions.slash_option(
        name="denomination",
        description="选择单位面额！每单位消耗一个劳动券与一个赞许。",
        required=True,
        opt_type=interactions.OptionType.INTEGER
    )
    async def set_money_painting_machine(self, ctx: interactions.SlashContext, coin_name: str, denomination: int):
        info = database_manager.query_item(ctx.user, '印钞机')

        if info[2] < 1:
            await ctx.send(f"您没有印钞机，不能做这件事。")
        elif '金圆券' in coin_name or denomination > 10000000000:
            await ctx.send(f"常凯申，你干的漂亮。")
        elif ('币' not in coin_name) and ('coin' not in coin_name):
            await ctx.send(f"名称中必须含有币或coin。")
        elif str(ctx.user) in coin_and_owner.load_dict():
            await ctx.send(f"你已经发行过{coin_and_owner.data[str(ctx.user)][0]}。")
        else:
            await ctx.send(f"成功发行{coin_name}！单位币值为{denomination}！")
            exchangeable_item.add_id(coin_name)
            coin_and_owner.add_kv(str(ctx.user), (coin_name, denomination))

    @module_base.subcommand("print_money",
                            sub_cmd_description="每份消耗一个赞许和一个劳动券")
    @interactions.slash_option(
        name="multiple",
        description="你要发行几份货币?",
        required=True,
        opt_type=interactions.OptionType.INTEGER
    )
    async def money_printing(self, ctx: interactions.SlashContext, multiple: int):
        info = database_manager.query_item(ctx.user, '印钞机')
        if info[2] < 1:
            await ctx.send("您没有印钞机，不能做这件事。")
        elif str(ctx.user) not in coin_and_owner.load_dict():
            await ctx.send("先设置发行纸币，再印钞！")
        elif database_manager.query_item(ctx.user, '赞许')[2] < multiple or \
                database_manager.query_item(ctx.user, '劳动券')[2] < multiple:
            await ctx.send("劳动券或赞许数量不够。")
        else:
            coin_name, denomination = coin_and_owner.data[str(ctx.user)]
            await ctx.send(f"开始印刷{coin_name}。")
            database_manager.update_item(ctx.user, '劳动券', -multiple)
            database_manager.update_item(ctx.user, '赞许', -multiple)
            database_manager.update_item(ctx.user, coin_name, multiple * denomination)
            await ctx.send(f"印刷完成，你发行了{multiple * denomination}个货币！")


class SetExchangeItems(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="exchange_items_manager",
        description="满足设置可交换物品的需求！"
    )

    @module_base.subcommand("add_item", sub_cmd_description="添加可交换物品。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="item_name",
        description="物品名",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def add_item(self, ctx: interactions.SlashContext, item_name: interactions.Role):
        await ctx.send(exchangeable_item.add_id(item_name))

    @module_base.subcommand("del_item", sub_cmd_description="移除可交换物品。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="item_name",
        description="物品名",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=False
    )
    async def del_item(self, ctx: interactions.SlashContext, item_name: interactions.Role):
        await ctx.send(exchangeable_item.remove_id(item_name))


class Gambling(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="gambling",
        description="看看你的运气如何！"
    )

    # 所有人指令：冷却三小时，进行一次风险劳动。
    @module_base.subcommand("risk_work", sub_cmd_description="看看你的运气，能不能获得更多劳动券！放心，期望是比一高的。")
    @interactions.cooldown(interactions.Buckets.USER, 1, 3 * 60 * 60)
    async def risk_work(self, ctx: interactions.SlashContext):
        # 该命令期望为1.1>1，冷却三小时。构成为 0.3*0+0.4*1+0.2*2+0.1*3=0.4+0.4+0.3
        if database_manager.query_item(ctx.user, '劳动券')[2] < 3:
            await ctx.send(f"劳动券不足三个，下次再来吧！")

        database_manager.update_item(ctx.user, '劳动券', -3)
        luck = random.random()
        if luck < 0.3:
            await ctx.send(f"看起来运气有点差，3个劳动券没了~下次或许能捞回来哦~")
        elif luck < 0.7:
            database_manager.update_item(ctx.user, '劳动券', 3)
            await ctx.send(f"嘿咻！看起来，你的劳动券没有变多，也没有变少。")

        elif luck < 0.9:
            database_manager.update_item(ctx.user, '劳动券', 6)
            await ctx.send(f"你的运气挺好啊，劳动券翻倍了！")
        elif luck < 0.9:
            database_manager.update_item(ctx.user, '劳动券', 9)
            await ctx.send(f"头奖！你的劳动券翻两番！快去好好炫耀一下吧！")

    @module_base.subcommand("risk_work", sub_cmd_description="看看你的运气，能不能获得更多劳动券！放心，期望是比一高的。")
    async def sell_your_gambling(self, ctx: interactions.SlashContext):
        # 该命令期望为1.1>1，冷却三小时。构成为 0.3*0+0.4*1+0.2*2+0.1*3=0.4+0.4+0.3
        if database_manager.query_item(ctx.user, '劳动券')[2] < 3:
            await ctx.send(f"劳动券不足三个，下次再来吧！")

        database_manager.update_item(ctx.user, '劳动券', -3)
        luck = random.random()
        if luck < 0.3:
            await ctx.send(f"看起来运气有点差，3个劳动券没了~下次或许能捞回来哦~")
        elif luck < 0.7:
            database_manager.update_item(ctx.user, '劳动券', 3)
            await ctx.send(f"嘿咻！看起来，你的劳动券没有变多，也没有变少。")

        elif luck < 0.9:
            database_manager.update_item(ctx.user, '劳动券', 6)
            await ctx.send(f"你的运气挺好啊，劳动券翻倍了！")
        elif luck < 0.9:
            database_manager.update_item(ctx.user, '劳动券', 9)
            await ctx.send(f"头奖！你的劳动券翻两番！快去好好炫耀一下吧！")


auto1 = Core.command_send_item
auto2 = Core.command_check_item


@auto1.autocomplete('item')
@auto2.autocomplete('item')
async def items_option_module_autocomplete(ctx: interactions.AutocompleteContext):
    items_option_input: str = ctx.input_text
    modules: list[str] = list(exchangeable_item.ids)
    modules_auto: list[str] = [
        i for i in modules if items_option_input in i
    ]

    await ctx.send(
        choices=[
            {
                "name": i,
                "value": i,
            } for i in modules_auto
        ]
    )
