🚀𝑻𝒆𝒍𝒆𝒎𝒆𝒕𝒓𝒚-𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏-𝒂𝒏𝒅-𝑨𝒈𝒈𝒓𝒆𝒈𝒂𝒕𝒊𝒐𝒏-𝑺𝒚𝒔𝒕𝒆𝒎
Real-Time System Monitoring Engine

Name: PRARTHANA D ACHARYA SRN: PES2UG24AM119

Name: NIHARIKA MIRLE      SRN: PES2UG24AM105

Name: NIDHI               SRN: PES2UG24AM102

🧠 What is this?

Telemetry Pulse is a fully automated, real-time observability system that continuously monitors your machine’s health and transforms it into interactive visual insights.

It captures:

CPU usage
Memory consumption
Disk activity
Network traffic

…and streams everything through a modern data pipeline to a live dashboard.

🏗️ Architecture at a Glance
Agent → Kafka → Consumer → InfluxDB → Grafana
Agent collects data
Kafka streams it reliably
Consumer processes it
InfluxDB stores it
Grafana visualizes it
📁 Project Blueprint
File	Purpose
run.py	Master orchestrator (runs everything)
agent.py	Collects system telemetry
consumer.py	Processes and stores data
docker-compose.yml	Spins up infrastructure
requirements.txt	Python dependencies
✨ Why This Project Stands Out
Real-time data streaming pipeline
Zero data loss architecture (Kafka buffering)
Live interactive dashboards
Fully automated setup (one command)
Modular and scalable design
🚀 One Command. Full System.
Step 1: Install dependencies
pip install -r requirements.txt
Step 2: Launch everything
python run.py
🎬 What Happens Behind the Scenes?

When you run run.py:

Infrastructure boots up (Kafka, Zookeeper, InfluxDB, Grafana)
The system waits until all services are available
Grafana is automatically configured
Data source connected
Dashboard created
The data pipeline starts
agent.py collects metrics
consumer.py processes and stores data
The dashboard opens automatically in your browser
📊 Dashboard

The system opens:

Automated Telemetry Dashboard

You can monitor:

CPU usage trends
Memory usage patterns
Overall system behavior
🔐 Default Login
Username: admin
Password: admin
🛑 Shutdown

Press:

Ctrl + C
Stops all scripts
Cleans up containers
Leaves no background processes
🔮 Future Enhancements
AI-based anomaly detection
Mobile monitoring interface
Cloud deployment
Smart alerting system
Multi-node distributed monitoring
💡 Inspiration

This project demonstrates how modern systems achieve observability by transforming system-level data into actionable insights.

🧑‍💻 Author Note

Built as part of a systems engineering mini-project exploring:

real-time data pipelines
distributed systems
observability tools
⭐ Final Thought

“If you can measure it, you can improve it.”
