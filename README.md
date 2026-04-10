🚀𝑻𝒆𝒍𝒆𝒎𝒆𝒕𝒓𝒚-𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏-𝒂𝒏𝒅-𝑨𝒈𝒈𝒓𝒆𝒈𝒂𝒕𝒊𝒐𝒏-𝑺𝒚𝒔𝒕𝒆𝒎
Real-Time System Monitoring Engine

Name: PRARTHANA D ACHARYA SRN: PES2UG24AM119

Name: NIHARIKA MIRLE      SRN: PES2UG24AM105

Name: NIDHI               SRN: PES2UG24AM102

Transform system metrics into live, actionable insights.
🧠 Overview

Telemetry Pulse is a fully automated observability pipeline that continuously monitors:

CPU • Memory • Disk • Network

and streams them into a real-time interactive dashboard.

🏗️ Architecture
Agent → Kafka → Consumer → InfluxDB → Grafana
Agent → collects system metrics
Kafka → ensures reliable streaming (no data loss)
Consumer → processes & forwards data
InfluxDB → stores time-series data
Grafana → visualizes insights
⚡ Quick Start
pip install -r requirements.txt
python run.py

✔ Spins up Docker services
✔ Starts data pipeline
✔ Auto-configures dashboard
✔ Opens Grafana instantly

📊 Features
Real-time monitoring
Automated setup (one command)
Scalable pipeline design
Zero data loss via Kafka buffering
📁 Key Files
File	Role
run.py	Orchestrates entire system
agent.py	Collects telemetry data
consumer.py	Processes & stores metrics
docker-compose.yml	Runs Kafka, InfluxDB, Grafana
🔐 Access
Username: admin
Password: admin
🔮 Future Scope

AI anomaly detection • Cloud deployment • Alerts • Multi-node monitoring

⭐

“If you can measure it, you can improve it.”
