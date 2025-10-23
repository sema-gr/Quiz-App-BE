import enum


class MembershipStatus(enum.Enum):
    MEMBER = "member"
    INVITED = "invited"
    REQUESTED = "requested"


class ActionType(enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    INVITE = "invite"
    REMOVE = "remove"
