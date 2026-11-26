"""Generate order lines whose totals exactly match orders.py."""
from events import run

if __name__ == '__main__':
    run('order_items')
