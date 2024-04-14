from app import run_pending_jobs, app

with app.app_context():
    run_pending_jobs()

# latest process id: kmcron
# tmux attach-session -t
# tmux ls
# tmux new -s kmcron
