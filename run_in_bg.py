from app import run_pending_jobs, app

with app.app_context():
    try:
        run_pending_jobs()
    except:
        pass

# latest process id: kmcron
# tmux attach-session -t
# tmux ls
# tmux new -s kmcron
