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
# 所有内容全都在该文件中处理
import os
from asyncio import tasks

import yaml


class SetManager:
    def __init__(self, file_path: str):
        self.data: set = set()
        self.file_path: str = file_path
        self.load()

    def load(self):
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            self.save()
            return self.data

    def save(self):
        with open(self.file_path, 'w') as f:
            yaml.dump(self.data, f, allow_unicode=True)


class DictManager:
    def __init__(self, file_path: str):
        self.data: dict = dict()
        self.file_path: str = file_path
        self.load()

    def load(self):
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            self.save()
            return self.data

    def save(self):
        with open(self.file_path, 'w') as f:
            yaml.dump(self.data, f, allow_unicode=True)

    def change(self, k, dv):
        self.data.setdefault(k, 0)
        self.data[k] += dv


import interactions
from interactions import SlashCommandChoice

from . import dataset

'''
The DEV_GUILD must be set to a specific guild_id
'''

# set类
admin_group = SetManager(f'{os.path.dirname(__file__)}/administer_roles.yaml')  # 存储有管理者权限的role id
not_exchangeable = SetManager(f'{os.path.dirname(__file__)}/not_exchangeable.yaml')  # 不可交换列表
item_crafting_table = SetManager(f'{os.path.dirname(__file__)}/item_crafting_table.yaml')  # 物品合成配方
# dict类
item_count_table = DictManager(f'{os.path.dirname(__file__)}/item_count_table .yaml')  # 物品数量表
item_attributes = DictManager(f'{os.path.dirname(__file__)}/item_attributes.yaml')  # 物品属性表
pending_orders = DictManager(f'{os.path.dirname(__file__)}/pending_orders.yaml')  # 交易挂单
gambling_orders = DictManager(f'{os.path.dirname(__file__)}/gambling_orders.yaml')  # 赌场挂单
currency_issuance_records = DictManager(f'{os.path.dirname(__file__)}/currency_issuance_records.yaml')  # 货币发行记录
not_exchangeable.data.update(('赞许', '点赞'))
item_attributes.data.update({
    '劳动券': {'等级': 1, '描述': '每天的签到带来的收获。'},
    '点赞': {'等级': 1, '描述': '送给你的赞许代表我爱你的心。'},
    '赞许': {'等级': 1, '描述': '不用客气，这是你应得的。'},
    '赌场券': {'等级': 3, '描述': '至少那些钱可以装到自己的口袋里了。'},
    '交易券': {'等级': 2, '描述': '卖东西了！'},
    '空气': {'等级': 0, '描述': '想不劳而获的下场就是这样。'},
    '印钞机': {'等级': 5, '描述': '一种神奇的只要投入少量努力就能无限印钞的机器。'}
})


async def administer_or_allowed_id(ctx: interactions.BaseContext):
    res: bool = await interactions.is_owner()(ctx)
    if os.environ.get("ROLE_ID"):
        if ctx.author.has_role(os.environ.get("ROLE_ID")): return True
    if ctx.author.guild_permissions.ADMINISTRATOR: return True
    ids: list = list(admin_group.data)
    if any(map(ctx.author.has_role, ids)): return True
    return False


# 合成方式：生成


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
        autocomplete=True
    )
    @interactions.slash_option(
        name="quantity",
        description="添加数量",
        required=True,
        opt_type=interactions.OptionType.NUMBER,
    )
    async def command_get_item(self, ctx: interactions.SlashContext, user_id: str, item: str,
                               quantity: int):
        user_id = str(user_id)
        item_count_table.change((user_id, item), quantity)
        await ctx.send(f"DEBUG:将{item}*{quantity}给予{user_id}")

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
        autocomplete=True
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
        sender_id = str(ctx.user)
        receiver_id = str(receiver_id)
        info = item_count_table.data[(sender_id, item)]
        if info[2] - quantity < 0:
            await ctx.send(f"您有{info[2]}个物品，您要发送{quantity}。数量不够，无法交易。")
            return
        item_count_table.data[sender_id, item] -= quantity
        item_count_table.data[receiver_id, item] -= quantity
        await ctx.send(f"交易成功！您赠送给{receiver_id} {quantity}个 {item}")

    @module_base.subcommand("show_item",
                            sub_cmd_description="显示自己某件物品或全部物品数量。")
    @interactions.slash_option(
        name="item",
        description="查看的特定物品，不填则为查看全部物品。",
        required=False,
        opt_type=interactions.OptionType.STRING,
        autocomplete=True
    )
    async def command_check_item(self, ctx: interactions.SlashContext, item: str = ''):
        user_id = str(ctx.user)
        if item == '':
            await ctx.send(
                '这是你全部物品列表：' + str([(k, v) for k, v in item_count_table.data.items() if user_id in k]))
        else:
            await ctx.send(f'您有{str(item_count_table.data.get((user_id, item), 0))}')

    @module_base.subcommand("get_all_data", sub_cmd_description="获取所有人和物品记录。")
    @interactions.check(administer_or_allowed_id)
    async def get_all(self, ctx: interactions.SlashContext):
        await ctx.send(str([(k, v) for k, v in item_count_table.data.items()]))

    @module_base.subcommand("add_role", sub_cmd_description="添加管理员身份组。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="role_id",
        description="身份组",
        required=True,
        opt_type=interactions.OptionType.ROLE
    )
    async def add_role(self, ctx: interactions.SlashContext, role_id: interactions.Role):
        admin_group.data.add(str(role_id.id))
        await ctx.send(f'添加身份组{role_id.id}')

    @module_base.subcommand("del_role", sub_cmd_description="删除管理员身份组。")
    @interactions.check(administer_or_allowed_id)
    @interactions.slash_option(
        name="role_id",
        description="身份组",
        required=True,
        opt_type=interactions.OptionType.ROLE
    )
    async def add_role(self, ctx: interactions.SlashContext, role_id: interactions.Role):
        admin_group.data.remove(str(role_id.id))
        await ctx.send(f'删除身份组{role_id.id}')
    @module_base.subcommand("save_data", sub_cmd_description="保存数据。")

    async def save_data(self, ctx: interactions.SlashContext):
        # set类
        admin_group.save()
        not_exchangeable.save()
        item_crafting_table.save()
        # dict类
        item_count_table.save()
        item_attributes.save()
        pending_orders.save()
        gambling_orders.save()
        currency_issuance_records.save()
        await  ctx.send("保存完成")


class Market(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="market",
        description="实时在线买卖您的商品！"
    )

    # region 填售卖单
    # 交易流程：每个人可以发送一个订单。订单包括：名称，售卖物品，单位数量，交换物品，单位数量，售卖单数。
    @module_base.subcommand("sell", sub_cmd_description="卖出您的商品！花费一个交易券，来填写你的售卖单。")
    @interactions.slash_option(
        name="item",
        description="产品名称",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=True
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
        autocomplete=True
    )
    @interactions.slash_option(
        name="exchange_num",
        description="交换数量",
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
                        exchange_num: int, max_count: int):
        seller_id = str(ctx.user)
        if item_count_table.data.get((seller_id, '交易券'), 0) < 1:
            await ctx.send("请先获取一个交易券。")
            return
        item_count_table.change((seller_id, "交易券"), -1)

        k = (seller_id, item, num, exchange_item, exchange_num)
        pending_orders.data[k] = max_count
        await ctx.send(f"您已经提交订单，以下是该订单的编号。\n{str(k)}")
    # endregion

    # region 使用售卖单
    # 普通人指令：买产品。
    @module_base.subcommand("buy",
                            sub_cmd_description="输入编号，买物品。有自动补全。")
    @interactions.slash_option(
        name="sell_id",
        description="售单id",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=True
    )
    @interactions.slash_option(
        name="multiple",
        description="交易多少单",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    async def buy_item(self, ctx: interactions.SlashContext, sell_id: str, multiple: int):
        if multiple <= 0:
            await ctx.send(f"必须大于零")
            return
        try:
            ticket = [i for i in pending_orders.data if str(i) == sell_id][0]
        except:
            await ctx.send("查无此单")
            return
        seller_id, item, num, exchange_item, exchange_num = ticket
        if pending_orders.data[sell_id][1] < multiple:
            await ctx.send(f"卖家单数不足，无法成交。")
            return
        sell_num = multiple * num
        buy_num = multiple * exchange_num
        buyer_id = str(ctx.user)
        if item_count_table.data.get((seller_id, item), 0) < sell_num or \
                item_count_table.data.get((buyer_id, exchange_item), 0) < buy_num:
            await ctx.send("物品不足，无法交易。")
            return
        item_count_table.change((seller_id, item), -sell_num)
        item_count_table.change((buyer_id, exchange_item), -buy_num)
        item_count_table.change((buyer_id, item), sell_num)
        item_count_table.change((seller_id, exchange_item), buy_num)
        await ctx.send("交易成功！祝您下次交易愉快！")
    # endregion


class Work(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="work",
        description="签到了，点赞了！"
    )

    # 所有人指令：卖你的产品！
    @module_base.subcommand("check_in", sub_cmd_description="获得你的点赞和劳动券！")
    @interactions.cooldown(interactions.Buckets.USER, 1, 15 * 60 * 60)
    async def check_in(self, ctx: interactions.SlashContext):
        user_id = str(ctx.user)
        item_count_table.change((user_id, '劳动券'), 3)
        item_count_table.change((user_id, '点赞'), 3)
        await ctx.send(f"您获得劳动券和点赞！")

    # 普通人指令：买产品。
    @module_base.subcommand("like",
                            sub_cmd_description="给你喜欢的人一个赞。")
    @interactions.slash_option(
        name="receiver_id",
        description="给他点赞",
        required=True,
        opt_type=interactions.OptionType.USER
    )
    async def like_sb(self, ctx: interactions.SlashContext, receiver_id: interactions.User):
        user_id = str(ctx.user)

        if item_count_table.data.get((user_id, '点赞')) < 1:
            await ctx.send(f"您没有点赞。通过签到获得。")
            return
        else:

            item_count_table.change((user_id, '点赞'), 3)
            item_count_table.change((receiver_id, '赞许'), 3)
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

        user_id = str(ctx.user)
        info = item_count_table.data.get((user_id, '印钞机'), 0)

        if info < 1:
            await ctx.send(f"您没有印钞机，不能做这件事。")
        elif '金圆券' in coin_name or denomination > 10000000000:
            await ctx.send(f"常凯申，你干的漂亮。")
        elif ('币' not in coin_name) and ('coin' not in coin_name):
            await ctx.send(f"名称中必须含有币或coin。")
        elif user_id in currency_issuance_records.data:
            await ctx.send(f"你已经发行过{currency_issuance_records.data[user_id][0]}。")
        else:
            await ctx.send(f"成功发行{coin_name}！单位币值为{denomination}！")
            item_attributes.data[coin_name] = {'等级': 5, '描述': '由少量努力打印的钞票。'}
            currency_issuance_records.data[user_id] = (coin_name, denomination)

    @module_base.subcommand("print_money",
                            sub_cmd_description="每份消耗一个赞许和一个劳动券")
    @interactions.slash_option(
        name="multiple",
        description="你要发行几份货币?",
        required=True,
        opt_type=interactions.OptionType.INTEGER
    )
    async def money_printing(self, ctx: interactions.SlashContext, multiple: int):
        user_id = str(ctx.user)
        if item_count_table.data.get((user_id, '印钞机'), 0) < 1:
            await ctx.send("您没有印钞机，不能做这件事。")
        elif user_id not in currency_issuance_records.data:
            await ctx.send("先设置发行纸币，再印钞！")
        elif item_count_table.data.get((user_id, '劳动券'), 0) < multiple or \
                item_count_table.data.get((user_id, '赞许'), 0) < multiple:
            await ctx.send("劳动券或赞许数量不够。")
        else:
            coin_name, denomination = currency_issuance_records.data[user_id]
            await ctx.send(f"开始印刷{coin_name}。")
            currency_issuance_records.change((user_id, '劳动券'), -multiple)
            currency_issuance_records.change((user_id, '赞许'), -multiple)
            currency_issuance_records.change((user_id, coin_name), multiple * denomination)
            await ctx.send(f"印刷完成，你发行了{multiple * denomination}个货币！")


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
        user_id = str(ctx.user)
        if item_count_table.data.get((user_id, '劳动券'),0) < 3:
            await ctx.send(f"劳动券不足三个，下次再来吧！")

        item_count_table.change((user_id, '劳动券'), -3)
        luck = random.random()
        if luck < 0.3:
            await ctx.send(f"看起来运气有点差，3个劳动券没了~下次或许能捞回来哦~")
        elif luck < 0.7:
            item_count_table.change((user_id, '劳动券'), 3)
            await ctx.send(f"嘿咻！看起来，你的劳动券没有变多，也没有变少。")

        elif luck < 0.9:
            item_count_table.change((user_id, '劳动券'), 6)
            await ctx.send(f"你的运气挺好啊，劳动券翻倍了！")
        else:
            item_count_table.change((user_id, '劳动券'), 9)
            await ctx.send(f"头奖！你的劳动券翻两番！快去好好炫耀一下吧！")

    """@module_base.subcommand("sell", sub_cmd_description="开您自定义的赌场！")
    @interactions.slash_option(
        name="types",
        description="赌博种类",
        required=True,
        opt_type=interactions.OptionType.STRING,
        choices=[
            SlashCommandChoice(name="掷骰子", value="掷骰子")
        ]
    )
    @interactions.slash_option(
        name="bet",
        description="基础赌注,100以下可能会出现错误。",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    @interactions.slash_option(
        name="item",
        description="赌博物品",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=True
    )
    @interactions.slash_option(
        name="odds",
        description="赔率，100代表期望为1。",
        required=True,
        opt_type=interactions.OptionType.INTEGER,
    )
    async def sell_gambling(self, ctx: interactions.SlashContext, types: str, bet: int, item: str,
                            odds: int):
        user_id =str( ctx.user)
        if item_count_table.data.get((user_id, '赌场券'), 0):
            await ctx.send("请先获取一个赌场券。")
            return
        item_count_table.change((user_id, '赌场券'), -1)

        k = (str(user_id), types, bet, item, odds)
        gambling_orders.data[str(k)]=k
        await ctx.send(f"您已经提交订单，以下是该订单的编号。\n{str(k)}")

    @module_base.subcommand("buy",
                            sub_cmd_description="输入编号，参加赌博。有自动补全。")
    @interactions.slash_option(
        name="sell_id",
        description="售单id",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=True
    )
    async def buy_gambling(self, ctx: interactions.SlashContext, sell_id: str):
        try:
            seller_id, types, bet, item, odds = dataset.gambling_manager.data[sell_id]
        except:
            await ctx.send("查无此单")
            return
        if types == "掷骰子":
            "最大收益四倍，最小收益零。"
            seller_bet = bet * odds / 100
            if item_count_table.data[seller_id, item)[2] < seller_bet or \
                    item_count_table.data[ctx.user, item)[2] < bet:
                await ctx.send("物品不足，无法开赌。")
                return

            a, b, c, d = [random.randint(0, 100) for _ in range(4)]
            await ctx.send(f"您掷出了{a},{b}")
            await ctx.send(f"您的对手掷出了{c},{d}")
            if a + b > c + d:
                database_manager.update_item(ctx.user, item, int(seller_bet))
                database_manager.update_item(seller_id, item, -int(seller_bet))
                await ctx.send(f"恭喜你！获得了{int(seller_bet)}个{item}！")
            if a + b == c + d:
                await ctx.send(f"平局！")
            if a + b < c + d:
                database_manager.update_item(ctx.user, item, -int(bet))
                database_manager.update_item(seller_id, item, int(bet))
                await ctx.send(f"你输掉了{bet}个{item}。下次再来或许会成功呢。")"""


auto1 = Core.command_send_item
auto2 = Core.command_check_item
auto3 = Market.sell_item
auto4 = Market.buy_item
auto5 =Core.command_get_item

@auto1.autocomplete('item')
@auto5.autocomplete('item')
@auto2.autocomplete('item')
@auto3.autocomplete('item')
@auto3.autocomplete('exchange_item')
async def items_option_module_autocomplete(self, ctx: interactions.AutocompleteContext):
    items_option_input: str = ctx.input_text
    modules: list[str] = list(item_attributes.data.keys())
    modules_auto: list[str] = [
        i for i in modules if items_option_input in i
    ]

    await ctx.send(
        choices=[
            {
                "name": i,
                "value": i,
            } for i in modules_auto if i not in not_exchangeable.data
        ]
    )


@auto4.autocomplete('sell_id')
async def sell_ticket_option_module_autocomplete(self, ctx: interactions.AutocompleteContext):
    items_option_input: str = ctx.input_text
    modules: list[tuple] = list(pending_orders.data.keys())
    modules_auto: list[str] = [
        str(i) for i in modules if items_option_input in pending_orders.data and pending_orders.data[i]>0
    ]

    await ctx.send(
        choices=[
            {
                "name": i,
                "value": i,
            } for i in modules_auto
        ]
    )


"""@auto6.autocomplete('sell_id')
async def sell_ticket_option_module_autocomplete(self, ctx: interactions.AutocompleteContext):
    items_option_input: str = ctx.input_text
    modules: list[str] = list(dataset.gambling_manager.data.keys())
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
    )"""
