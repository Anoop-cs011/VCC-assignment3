#!/bin/bash

# get cpu usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')
echo "CPU Usage: $CPU_USAGE%"

# check if CPU usage exceeds 45%
if (( $(echo "$CPU_USAGE > 45" | bc -l) )); then
	echo "CPU usage exceeds 45%, creating a new instance group in VM"
	gcloud beta compute instance-groups managed create vcc3scaling --project=vcc-assg3 --base-instance-name=vcc3scaling1 --template=projects/vcc-assg3/regions/us-central1/instanceTemplates/vcc3scalable --size=1 --zone=us-central1-c --default-action-on-vm-failure=repair --action-on-vm-failed-health-check=default-action --no-force-update-on-repair --standby-policy-mode=manual --list-managed-instances-results=pageless && gcloud beta compute instance-groups managed set-autoscaling vcc3scaling --project=vcc-assg3 --zone=us-central1-c --mode=on --min-num-replicas=1 --max-num-replicas=3 --target-cpu-utilization=0.75 --cpu-utilization-predictive-method=none --cool-down-period=60
	
	# running the app on the instance group
	gcloud compute ssh $(gcloud compute instance-groups list-instances vcc3scaling --region=your-region --format="value(instance)") --command="gunicorn --bind 0.0.0.0:5000 mainApp:app"
fi
