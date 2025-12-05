module.exports = {
    apps: [
        {
            name: "market-data-service",
            script: ".venv/bin/uvicorn",
            args: "src.api.server:app --host 0.0.0.0 --port 8010",
            interpreter: "none",
            cwd: "/home/rford/caelum/caelum-supersystem/market-data-service",
            env: {
                PORT: 8010,
                PYTHONPATH:
                    "/home/rford/caelum/caelum-supersystem/market-data-service",
            },
            out_file: "/home/rford/.pm2/logs/market-data-out.log",
            error_file: "/home/rford/.pm2/logs/market-data-error.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            autorestart: true,
            watch: false,
            max_memory_restart: "500M",
            instances: 1,
            exec_mode: "fork",
        },
    ],
};
