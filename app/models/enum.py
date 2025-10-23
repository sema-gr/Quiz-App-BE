import enum


class MembershipStatus(enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"


class MembershipAction(enum.Enum):
    INVITE = "invite"
    ACCEPT = "accept"
    REMOVE = "remove"
