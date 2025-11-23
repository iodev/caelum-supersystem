#!/bin/bash
# Launch Parallel Claude Code Sessions
# Created: 2025-10-26 23:00

echo "🚀 Launching Parallel Claude Code Sessions..."
echo ""

# Check if we're on .27
if [ "$(hostname)" != "caelum" ]; then
    echo "⚠️  Warning: Expected to run on caelum (10.32.3.27)"
    echo "   Current host: $(hostname)"
    echo ""
fi

# Session 1: This session (already running)
echo "Session 1: FinVec Data Generation Monitoring"
echo "  Status: ✅ Already running (this session)"
echo "  Task: Monitor seq300, prepare parallel generation"
echo ""

# Session 2: PIM Phase 2 Testing
echo "Session 2: PIM Phase 2 Testing & Integration"
echo "  Launch: cd /home/rford/caelum/ss/PassiveIncomeMaximizer && claude-code"
echo "  Task: Test Caelum client, create auto-storage for predictions"
echo "  Duration: ~30 minutes"
echo ""
read -p "Press Enter to open Session 2 in new terminal..."
gnome-terminal --tab --title="PIM Phase 2" -- bash -c "cd /home/rford/caelum/ss/PassiveIncomeMaximizer && claude-code; exec bash" &

# Session 3: caelum-unified Development
echo "Session 3: caelum-unified Supervisor Development"
echo "  Launch: cd /home/rford/caelum/ss/caelum-unified && claude-code"
echo "  Task: Debug Ollama CUDA error, create Infrastructure Supervisor"
echo "  Duration: ~40 minutes"
echo ""
read -p "Press Enter to open Session 3 in new terminal..."
gnome-terminal --tab --title="caelum-unified" -- bash -c "cd /home/rford/caelum/ss/caelum-unified && claude-code; exec bash" &

echo ""
echo "✅ Parallel sessions launched!"
echo ""
echo "📋 Next Steps:"
echo "  1. In Session 2 (PIM), ask Claude to:"
echo "     'Test the Caelum client integration and create auto-storage for FinVec predictions'"
echo ""
echo "  2. In Session 3 (caelum-unified), ask Claude to:"
echo "     'Debug the .44 Ollama CUDA error and create the Infrastructure Supervisor'"
echo ""
echo "  3. This session will monitor seq300 and prepare parallel data generation"
echo ""
echo "⏰ When seq300 completes (~15 min), we'll launch parallel generation on .27, .44, .62"
echo ""
