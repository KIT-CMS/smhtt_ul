#!/bin/bash
MODE=${1}
SESSION_NAME="sfs_v15_cmssw"
# SCRIPTS=("make_sfs_16pre.sh" "make_sfs_17.sh" "make_sfs_18.sh")
SCRIPTS=("make_sfs_16post.sh" "make_sfs_17.sh" "make_sfs_18.sh")
# WINDOW_NAMES=("16pre" "17" "18")
WINDOW_NAMES=("16post" "17" "18")
TARGET_DIR="/work/jvoss/smhtt_ul_SFs_v15"

# 1. Create or ensure the session exists
if ! tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
    tmux new-session -d -s "${SESSION_NAME}" -n "${WINDOW_NAMES[0]}" -c "${TARGET_DIR}"
    sleep 0.3  # Let session initialize
fi

# 2. Iterate through each window and ensure it is ready
for i in "${!SCRIPTS[@]}"; do
    W_NAME="${WINDOW_NAMES[$i]}"
    
    # Skip creating the first window if it's already there
    if [ "$i" -ne 0 ]; then
        # Check if window exists by name. If not, create it.
        if ! tmux list-windows -t "${SESSION_NAME}" -F "#{window_name}" | grep -qx "${W_NAME}"; then
            tmux new-window -d -t "${SESSION_NAME}" -n "${W_NAME}" -c "${TARGET_DIR}"
            sleep 0.5  # Increased delay for window initialization
        fi
    fi
    
    # 3. Send commands to the confirmed window
    TARGET="${SESSION_NAME}:${W_NAME}"
    
    # Fixed: Separate C-c from the clear command
    tmux send-keys -t "${TARGET}" C-c
    sleep 1
    tmux send-keys -t "${TARGET}" "cd ${TARGET_DIR} && ./${SCRIPTS[$i]} ${MODE}" Enter
done

# 4. Attach to session - switch to first window
tmux select-window -t "${SESSION_NAME}:${WINDOW_NAMES[0]}"
tmux attach-session -t "${SESSION_NAME}"