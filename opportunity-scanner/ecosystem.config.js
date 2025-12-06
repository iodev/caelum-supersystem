module.exports = {
    apps: [
        {
            name: "opportunity-scanner",
            script: ".venv/bin/uvicorn",
            args: "src.api.server:app --host 0.0.0.0 --port 8011",
            interpreter: "none",
            cwd: "/home/rford/caelum/caelum-supersystem/opportunity-scanner",
            env: {
                PORT: 8011,
                PYTHONPATH: "/home/rford/caelum/caelum-supersystem/opportunity-scanner",
                MARKET_DATA_SERVICE_URL: "http://10.32.3.27:8010"
            },
            out_file: "/home/rford/.pm2/logs/opportunity-scanner-out.log",
            error_file: "/home/rford/.pm2/logs/opportunity-scanner-error.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            autorestart: true,
            watch: false,
            max_memory_restart: "500M",
            instances: 1,
            exec_mode: "fork",
        },
    ],
};
