"""
Core data classes for the simulation.

These are deliberately simple (plain dataclasses) -- the interesting data
structure work happens in registry.py, order_queue.py, graph.py and
dispatch.py, not here. Don't over-engineer this file.
"""

from dataclasses import dataclass, field
from enum import Enum


class OrderStatus(Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    QUEUED = "queued"
    PREPARING = "preparing"
    RIDER_ASSIGNED = "rider_assigned"
    AWAITING_RIDER = "awaiting_rider"
    PICKED_UP = "picked_up"
    ON_THE_WAY = "on_the_way"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class RiderStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


class PaymentMethod(Enum):
    COD = "cod"
    UPI = "upi"
    CARD = "card"


class RefundStatus(Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class PaymentRecord:
    payment_id: str
    method: PaymentMethod | str
    amount: float
    status: str = "completed"  # completed, pending_cod, refunded
    details: str = ""
    timestamp: str = ""


@dataclass
class RefundRecord:
    refund_id: str
    order_id: str
    amount: float
    method: str
    status: RefundStatus | str = RefundStatus.INITIATED
    reason: str = ""
    created_at: str = ""
    updated_at: str = ""
    account_destination: str = ""


@dataclass
class Customer:
    id: str
    name: str
    location: str  # must match a node name in the LocationGraph


@dataclass
class Restaurant:
    id: str
    name: str
    location: str  # must match a node name in the LocationGraph


@dataclass
class Rider:
    id: str
    name: str
    current_location: str  # must match a node name in the LocationGraph
    status: RiderStatus = RiderStatus.IDLE

    # TODO (optional/extra): track something like `idle_since` timestamp if
    # you want "longest-idle rider" as a tie-breaker in dispatch.py.


@dataclass
class Order:
    id: str
    customer: Customer
    restaurant: Restaurant
    is_urgent: bool = False
    status: OrderStatus = OrderStatus.PLACED
    assigned_rider: Rider | None = None
    route: list[str] = field(default_factory=list)
    eta_minutes: float | None = None
    payment: PaymentRecord | None = None
    refund: RefundRecord | None = None

