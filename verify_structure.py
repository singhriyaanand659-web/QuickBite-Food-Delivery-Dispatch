"""Checks that the project imports and required symbols exist."""

from dispatch import select_best_rider_heap, select_best_rider_linear_scan
from graph import LocationGraph
from models import Customer, Order, OrderStatus, Restaurant, Rider, RiderStatus
from order_queue import RestaurantOrderQueue, UrgentOrderQueue
from registry import Registry

print("Project structure imports successfully.")
print("Core functions are present. Complete the TODOs before running the full simulation.")
