"""
調整さんのイベント、参加者、出欠などのデータ構造を定義するモジュール。
"""
from dataclasses import dataclass, field
from enum import Enum

class Attendance(Enum):
    """出欠のステータスを表す列挙型"""
    ATTENDING = '○'
    MAYBE = '△'
    ABSENT = '×'
    UNKNOWN = ''

    @classmethod
    def from_str(cls, value: str) -> 'Attendance':
        """文字列から対応するEnumメンバーを返す"""
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN

@dataclass(frozen=True)
class Schedule:
    """一つの日程候補を表すデータクラス"""
    datetime: str

@dataclass
class Participant:
    """参加者一人を表すデータクラス"""
    name: str
    comment: str
    # key: Schedule object, value: Attendance object
    attendances: dict[Schedule, Attendance] = field(default_factory=dict)

@dataclass
class Event:
    """調整さんのイベント全体を表すデータクラス"""
    title: str
    description: str
    schedules: list[Schedule] = field(default_factory=list)
    participants: list[Participant] = field(default_factory=list)
