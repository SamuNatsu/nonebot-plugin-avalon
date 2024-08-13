from enum import Enum, auto, unique


@unique
class RoleEnum(Enum):
  MERLIN   = auto()
  PERCIVAL = auto()
  SERVANT  = auto()
  MORDRED  = auto()
  MORGANA  = auto()
  ASSASSIN = auto()
  OBERON   = auto()
  LACHEY   = auto()


ROLE_NAME: dict[RoleEnum, str] = {
  RoleEnum.MERLIN:   "🔵梅林",
  RoleEnum.PERCIVAL: "🔵派西维尔",
  RoleEnum.SERVANT:  "🔵亚瑟的忠臣",
  RoleEnum.MORDRED:  "🔴莫德雷德",
  RoleEnum.MORGANA:  "🔴莫甘娜",
  RoleEnum.ASSASSIN: "🔴刺客",
  RoleEnum.OBERON:   "🔴奥伯伦",
  RoleEnum.LACHEY:   "🔴莫德雷德的爪牙",
}

ROLE_HELP: dict[RoleEnum, str] = {
  RoleEnum.MERLIN:   "知道谁是邪恶方，但必须隐藏好自己的身份",
  RoleEnum.PERCIVAL: "知道谁是梅林",
  RoleEnum.SERVANT:  "帮助正义方获得胜利",
  RoleEnum.MORDRED:  "梅林不知道他",
  RoleEnum.MORGANA:  "在派西维尔眼中以梅林的形象出现",
  RoleEnum.ASSASSIN: "随时可以进行刺杀，若成功刺杀梅林，则邪恶方获胜，否则正义方获胜",
  RoleEnum.OBERON:   "对邪恶方来说彼此互不了解",
  RoleEnum.LACHEY:   "帮助邪恶方获得胜利",
}

ROLE_SET: dict[int, list[RoleEnum]] = {
  5: [
    RoleEnum.MERLIN, RoleEnum.PERCIVAL, RoleEnum.SERVANT,
    RoleEnum.MORGANA, RoleEnum.ASSASSIN,
  ],
  6: [
    RoleEnum.MERLIN, RoleEnum.PERCIVAL, RoleEnum.SERVANT, RoleEnum.SERVANT,
    RoleEnum.MORGANA, RoleEnum.ASSASSIN,
  ],
  7: [
    RoleEnum.MERLIN, RoleEnum.PERCIVAL, RoleEnum.SERVANT, RoleEnum.SERVANT,
    RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.OBERON,
  ],
  8: [
    RoleEnum.MERLIN, RoleEnum.PERCIVAL,
    RoleEnum.SERVANT, RoleEnum.SERVANT, RoleEnum.SERVANT,
    RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.LACHEY,
  ],
  9: [
    RoleEnum.MERLIN, RoleEnum.PERCIVAL,
    RoleEnum.SERVANT, RoleEnum.SERVANT, RoleEnum.SERVANT, RoleEnum.SERVANT,
    RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.MORDRED,
  ],
  10: [
    RoleEnum.MERLIN, RoleEnum.PERCIVAL,
    RoleEnum.SERVANT, RoleEnum.SERVANT, RoleEnum.SERVANT, RoleEnum.SERVANT,
    RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.MORDRED, RoleEnum.OBERON,
  ],
}

ROLE_SET_NAME: dict[int, str] = {
  5: "梅林、派西维尔、亚瑟的忠臣\n⚔️\n莫甘娜、刺客",
  6: "梅林、派西维尔、亚瑟的忠臣x2\n⚔️\n莫甘娜、刺客",
  7: "梅林、派西维尔、亚瑟的忠臣x2\n⚔️\n莫甘娜、刺客、奥伯伦",
  8: "梅林、派西维尔、亚瑟的忠臣x3\n⚔️\n莫甘娜、刺客、莫德雷德的爪牙",
  9: "梅林、派西维尔、亚瑟的忠臣x4\n⚔️\n莫甘娜、刺客、莫德雷德",
  10: "梅林、派西维尔、亚瑟的忠臣x4\n⚔️\n莫甘娜、刺客、莫德雷德、奥伯伦",
}
