from . import StateEnum
from ..game import Game
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import UniMessage, on_alconna
from nonebot_plugin_session import EventSession, SessionLevel


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  self.vote = {}

  # State-scope matcher handlers
  async def handle_agree(session: EventSession) -> None:
    # Group msg & Is room & Is player
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 in self.players
    ):
      await self.on_msg(type="agree", user_id=session.id1)

  async def handle_disagree(session: EventSession) -> None:
    # Group msg & Is room & Is player
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 in self.players
    ):
      await self.on_msg(type="disagree", user_id=session.id1)

  # Create matchers
  self.matchers["agree"] = on_alconna(".awl同意", handlers=[handle_agree])
  self.matchers["disagree"] = on_alconna(".awl反对", handlers=[handle_disagree])

  await (
    UniMessage
      .text(f"📣请投票表决第{self.round + 1}轮出征队伍\n")
      .text(f"⌛尝试组队次数：{self.build_tries}/5\n")
      .text(f"👑队长：{self.players[self.leader].name}\n")
      .text("[.awl同意] 投同意票\n")
      .text("[.awl反对] 投反对票")
      .send(reply_to=True)
    )

# On message
async def msg(self: Game, type: str, user_id: str) -> None:
  if user_id in self.vote:
    await (
      UniMessage
        .text(f"⚠️你已经对该队伍投了 {"[✅同意票]" if self.vote[user_id] else "[❎反对票]"}]")
        .send(reply_to=True)
    )
    return

  def vote_count() -> tuple[int, int, int]:
    agree: int = len(list(filter(lambda x: x, self.vote.values())))
    disagree: int = len(list(filter(lambda x: not x, self.vote.values())))
    return (agree, len(self.players) - agree - disagree, disagree)

  if type == "agree":
    self.vote[user_id] = True
    agree, none, disagree = vote_count()
    await (
      UniMessage
        .text(f"📣[{self.players[user_id].name}] 投了 [✅同意票]\n")
        .text(f"当前票型：{"🟩" * agree}{"⬜" * none}{"🟥" * disagree}")
        .send(reply_to=True)
    )
  else:
    self.vote[user_id] = False
    agree, none, disagree = vote_count()
    await (
      UniMessage
        .text(f"📣[{self.players[user_id].name}] 投了 [❎反对票]\n")
        .text(f"当前票型：{"🟩" * agree}{"⬜" * none}{"🟥" * disagree}")
        .send(reply_to=True)
    )

  agree, none, disagree = vote_count()
  if agree / len(self.players) > 0.5:
    await (
      UniMessage
        .text(f"✅队伍通过了投票\n")
        .text(f"🟩TA们投了同意：\n{
          "\n".join(
            map(
              lambda x: self.players[x[0]].name,
              filter(lambda x: x[1], self.vote.items())
            )
          )
        }\n")
        .text(f"🟥TA们投了反对：\n{
          "\n".join(
            map(
              lambda x: self.players[x[0]].name,
              filter(lambda x: not x[1], self.vote.items())
            )
          )
        }\n")
        .send(self.guild_target)
    )
    await self.to_state(StateEnum.TEAM_SET_OUT)

  if disagree / len(self.players) > 0.5:
    await (
      UniMessage
        .text(f"❎队伍未通过投票\n")
        .text(f"🟩TA们投了同意：\n{
          "\n".join(
            map(
              lambda x: self.players[x[0]].name,
              filter(lambda x: x[1], self.vote.items())
            )
          )
        }\n")
        .text(f"🟥TA们投了反对：\n{
          "\n".join(
            map(
              lambda x: self.players[x[0]].name,
              filter(lambda x: not x[1], self.vote.items())
            )
          )
        }\n")
        .send(self.guild_target)
    )
    await self.to_state(StateEnum.NEXT_LEADER)

# On exit
async def exit(self: Game, _: StateEnum) -> None:
  self.remove_matchers("agree", "disagree")

# Register state
Game.register_state(
  State(StateEnum.TEAM_VOTE, enter=enter, msg=msg, exit=exit)
)
