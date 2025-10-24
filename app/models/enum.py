import enum


class MembershipStatus(enum.Enum):
    ACCEPTED = "accepted"
    PENDING = "pending"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class MembershipAction(enum.Enum):
    INVITE = "invite"
    REQUEST = "request"
