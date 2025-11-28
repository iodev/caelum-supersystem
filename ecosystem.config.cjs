// Caelum SuperSystem PM2 Configuration
// Services that support PassiveIncomeMaximizer

module.exports = {
  apps: [
    // FinColl V7 - ML Predictions API (Port 8002)
    {
      name: 'fincoll-v7',
      script: '.venv/bin/uvicorn',
      args: 'fincoll.server:app --host 0.0.0.0 --port 8002',
      cwd: '/home/rford/caelum/ss/fincoll',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',  // ML models are large
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // SenVec Aggregator - Main sentiment API (Port 18000)
    {
      name: 'senvec-aggregator',
      script: '.venv/bin/uvicorn',
      args: 'services.aggregator.app:app --host 0.0.0.0 --port 18000',
      cwd: '/home/rford/caelum/ss/senvec',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // SenVec SentimenTrader (Port 18001)
    {
      name: 'senvec-sentimentrader',
      script: '.venv/bin/uvicorn',
      args: 'services.sentimentrader.app:app --host 0.0.0.0 --port 18001',
      cwd: '/home/rford/caelum/ss/senvec',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // SenVec AlphaVantage (Port 18002)
    {
      name: 'senvec-alphavantage',
      script: '.venv/bin/uvicorn',
      args: 'services.alphavantage.app:app --host 0.0.0.0 --port 18002',
      cwd: '/home/rford/caelum/ss/senvec',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // SenVec Social (Port 18003)
    {
      name: 'senvec-social',
      script: '.venv/bin/uvicorn',
      args: 'services.social.app:app --host 0.0.0.0 --port 18003',
      cwd: '/home/rford/caelum/ss/senvec',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // SenVec News (Port 18004)
    {
      name: 'senvec-news',
      script: '.venv/bin/uvicorn',
      args: 'services.news.app:app --host 0.0.0.0 --port 18004',
      cwd: '/home/rford/caelum/ss/senvec',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // Vue3 Development Server (Port 5500) - Optional for dev
    {
      name: 'pim-vue3-dev',
      script: 'yarn',
      args: 'vue',
      cwd: '/home/rford/caelum/ss/PassiveIncomeMaximizer',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development'
      }
    }
  ]
};
