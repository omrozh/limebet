from app import run_pending_jobs, app
from betting_utils import live_betting, register_open_bet
import time

total_minutes = 0

with app.app_context():
    while True:
        print(total_minutes)
        if total_minutes == 120:
            try:
                register_open_bet()
            except:
                pass
            total_minutes = 0
        try:
            live_betting()
        except:
            pass
        total_minutes += 1
        time.sleep(60)

# latest process id: kmcron
# tmux attach-session -t kmcron
# tmux kill-session -t kmcron
# tmux ls
# tmux new -s kmcron
