import enum


class OrderStatus(enum.Enum):
    NEW = 'NEW'
    DELIVERY = 'DELIVERY'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    REFUND = 'REFUND'
