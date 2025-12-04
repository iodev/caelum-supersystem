/**
 * PM2 Ecosystem Configuration for PassiveIncomeMaximizer System
 *
 * This configures all critical services to auto-start on system reboot
 * CRITICAL: Required for position management during reboots
 */

module.exports = {
    apps: [
        // =========================================================================
        // CORE PIM SERVER - HIGHEST PRIORITY
        // Manages active positions and trades
        // =========================================================================
        {
            name: "pim-server",
            cwd: "/home/rford/caelum/ss/PassiveIncomeMaximizer",
            script: "./node_modules/.bin/tsx",
            args: "server/index.ts",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "2G",
            env: {
                NODE_ENV: "development",
                PIM_SERVER_PORT: "5000",
                DATABASE_URL:
                    "postgresql://pim_user:pim_secure_2025!@localhost:15433/pim_database",
            },
            error_file:
                "/home/rford/caelum/ss/PassiveIncomeMaximizer/logs/pim-error.log",
            out_file:
                "/home/rford/caelum/ss/PassiveIncomeMaximizer/logs/pim-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            // Wait for dependencies before starting
            wait_ready: true,
            listen_timeout: 30000,
            // Restart immediately if crashes (active positions!)
            min_uptime: 5000,
            max_restarts: 50,
            restart_delay: 2000,
        },

        // =========================================================================
        // FINCOLL - ML INFERENCE API
        // Provides ML predictions to agents (includes finvec+senvec internally)
        // =========================================================================
        {
            name: "fincoll-server",
            cwd: "/home/rford/caelum/ss/fincoll",
            script: "/home/rford/caelum/ss/fincoll/.venv/bin/python",
            args: "-m fincoll.server",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "2G",
            env: {
                PYTHONUNBUFFERED: "1",
                FINCOLL_HOST: "0.0.0.0",
                FINCOLL_PORT: "8002",
                CUDA_VISIBLE_DEVICES: "0", // Enable GPU/CUDA acceleration
            },
            error_file: "/home/rford/caelum/ss/fincoll/logs/fincoll-error.log",
            out_file: "/home/rford/caelum/ss/fincoll/logs/fincoll-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 10000,
            max_restarts: 10,
            restart_delay: 5000,
        },

        // =========================================================================
        // SENVEC MICROSERVICES - SENTIMENT ANALYSIS (49D active, 72D potential)
        // Note: SentimentTrader (23D) disabled - $99/month cost, requires manual CSV setup
        // =========================================================================
        //  // SentimentTrader - 23D market sentiment (f187-f209)
        //  {
        //  name: 'senvec-sentimentrader',
        //  cwd: '/home/rford/caelum/ss/senvec/services/sentimentrader',
        //  script: '/home/rford/caelum/ss/senvec/.venv/bin/uvicorn',
        //  args: 'app:app --host 0.0.0.0 --port 18001',
        //  interpreter: 'none',
        //  instances: 1,
        //  autorestart: true,
        //  watch: false,
        //  max_memory_restart: '512M',
        //  env: {
        //  PYTHONUNBUFFERED: '1',
        //  },
        //  error_file: '/home/rford/caelum/ss/senvec/logs/sentimentrader-error.log',
        //  out_file: '/home/rford/caelum/ss/senvec/logs/sentimentrader-out.log',
        //  log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
        //  min_uptime: 5000,
        //  max_restarts: 10,
        //  restart_delay: 3000,
        //  },
        //
        // Alpha Vantage - 18D cross-asset signals (f210-f227)
        {
            name: "senvec-alphavantage",
            cwd: "/home/rford/caelum/ss/senvec/services/alphavantage",
            script: "/home/rford/caelum/ss/senvec/.venv/bin/uvicorn",
            args: "app:app --host 0.0.0.0 --port 18002",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "512M",
            env: {
                PYTHONUNBUFFERED: "1",
            },
            error_file:
                "/home/rford/caelum/ss/senvec/logs/alphavantage-error.log",
            out_file: "/home/rford/caelum/ss/senvec/logs/alphavantage-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 5000,
            max_restarts: 10,
            restart_delay: 3000,
        },

        // Social Sentiment - 23D social media (f228-f250)
        {
            name: "senvec-social",
            cwd: "/home/rford/caelum/ss/senvec/services/social",
            script: "/home/rford/caelum/ss/senvec/.venv/bin/uvicorn",
            args: "app:app --host 0.0.0.0 --port 18003",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "512M",
            env: {
                PYTHONUNBUFFERED: "1",
            },
            error_file: "/home/rford/caelum/ss/senvec/logs/social-error.log",
            out_file: "/home/rford/caelum/ss/senvec/logs/social-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 5000,
            max_restarts: 10,
            restart_delay: 3000,
        },

        // News Sentiment - 8D news sentiment (f251-f258)
        {
            name: "senvec-news",
            cwd: "/home/rford/caelum/ss/senvec/services/news",
            script: "/home/rford/caelum/ss/senvec/.venv/bin/uvicorn",
            args: "app:app --host 0.0.0.0 --port 18004",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "512M",
            env: {
                PYTHONUNBUFFERED: "1",
            },
            error_file: "/home/rford/caelum/ss/senvec/logs/news-error.log",
            out_file: "/home/rford/caelum/ss/senvec/logs/news-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 5000,
            max_restarts: 10,
            restart_delay: 3000,
        },

        // SenVec Aggregator - Combines all 4 services into 72D
        {
            name: "senvec-aggregator",
            cwd: "/home/rford/caelum/ss/senvec/services/aggregator",
            script: "/home/rford/caelum/ss/senvec/.venv/bin/uvicorn",
            args: "app:app --host 0.0.0.0 --port 18000",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "1G",
            env: {
                PYTHONUNBUFFERED: "1",
                PORT: "18000",
                REDIS_HOST: "10.32.3.27",
                REDIS_PORT: "6379",
            },
            error_file:
                "/home/rford/caelum/ss/senvec/logs/aggregator-error.log",
            out_file: "/home/rford/caelum/ss/senvec/logs/aggregator-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 10000,
            max_restarts: 10,
            restart_delay: 5000,
        },

        // =========================================================================
        // AUTONOMOUS SYSTEMS - SELF-IMPROVEMENT & SELF-REPAIR
        // =========================================================================

        // Adaptive Backtest Scheduler - Automatically backtests and adjusts strategy
        {
            name: "adaptive-scheduler",
            cwd: "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine",
            script: "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine/.venv/bin/python",
            args: "-m pim.workflows.adaptive_scheduler --daemon --min-check 5 --max-check 360 --backoff 5",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "1G",
            env: {
                PYTHONUNBUFFERED: "1",
                DATABASE_URL:
                    "postgresql://pim_user:pim_secure_2025!@10.32.3.27:15433/pim_database",
            },
            error_file:
                "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine/logs/adaptive-scheduler-error.log",
            out_file:
                "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine/logs/adaptive-scheduler.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 5000,
            max_restarts: 10,
            restart_delay: 5000,
        },

        // Self-Repair System - Detects bugs and fixes code automatically
        {
            name: "self-repair",
            cwd: "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine",
            script: "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine/.venv/bin/python",
            args: "-m pim.workflows.self_repair --monitor",
            interpreter: "none",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "1G",
            env: {
                PYTHONUNBUFFERED: "1",
                DATABASE_URL:
                    "postgresql://pim_user:pim_secure_2025!@10.32.3.27:15433/pim_database",
                ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
                OPENAI_API_KEY: process.env.OPENAI_API_KEY,
                XAI_API_KEY: process.env.XAI_API_KEY,
            },
            error_file:
                "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine/logs/self-repair-error.log",
            out_file:
                "/home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine/logs/self-repair.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            min_uptime: 5000,
            max_restarts: 10,
            restart_delay: 5000,
        },
    ],
};
