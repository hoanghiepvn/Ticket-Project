"""Generate payment attempts with retries and at most one successful payment per order."""
from events import run

if __name__ == '__main__':
    run('payments')
