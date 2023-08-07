# !/bin/sh

tmux new -s cosine -d

# working window
tmux send-keys 'vim' C-m

# client dev window
tmux split-window -v -t cosine
tmux resize-pane -D 10
tmux send-keys 'make dev' C-m 'n' C-m

# git/misc window
tmux new-window -t cosine

tmux select-window -t cosine:0
tmux select-pane -t 0
tmux a -t cosine
