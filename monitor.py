import subprocess
import psutil
import time

# GCP Configurations
PROJECT_ID = "vcc-assg3"
ZONE = "us-central1-c"
REGION = "us-central1"
INSTANCE_TEMPLATE = "projects/vcc-assg3/regions/us-central1/instanceTemplates/vcc3scalable"  # Pre-configured instance template
INSTANCE_GROUP_NAME = "vcc3scaling"
CPU_THRESHOLD_UP = 45  # Scale-up threshold (%)
CHECK_INTERVAL = 10  # Check CPU every 10 seconds
APP_COMMAND = "gunicorn --bind 0.0.0.0:5000 app:app"

def create_instance_group():
    """Creates a GCP Managed Instance Group if it doesn't exist and enables auto-scaling."""
    try:
        # Check if instance group already exists
        check_cmd = [
            "gcloud", "compute", "instance-groups", "managed", "describe",
            INSTANCE_GROUP_NAME, "--zone", ZONE, "--project", PROJECT_ID
        ]
        result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if "NOT_FOUND" in result.stderr:
            print("[INFO] Instance group not found, creating a new one...")
            
            # Create instance group from a template
            create_cmd = [
                "gcloud", "compute", "instance-groups", "managed", "create", INSTANCE_GROUP_NAME,
                "--template", INSTANCE_TEMPLATE, "--size", "1", "--zone", ZONE, "--project", PROJECT_ID
            ]
            subprocess.run(create_cmd, check=True)
            print("[SUCCESS] Instance Group Created!")

            # Enable auto-scaling
            enable_autoscaling()

            # Run the application on the new instance
            start_application()

        else:
            print("[INFO] Instance group already exists. Ensuring auto-scaling is enabled...")
            enable_autoscaling()
            start_application()

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create instance group: {e}")

def enable_autoscaling():
    """Enables auto-scaling on the instance group."""
    try:
        autoscale_cmd = [
            "gcloud", "beta", "compute", "instance-groups", "managed", "set-autoscaling", INSTANCE_GROUP_NAME,
            "--project", PROJECT_ID, "--zone", ZONE,
            "--mode", "on", "--min-num-replicas", "1", "--max-num-replicas", "3",
            "--target-cpu-utilization", "0.75",
            "--cool-down-period", "60"
        ]
        subprocess.run(autoscale_cmd, check=True)
        print("[SUCCESS] Auto-scaling enabled!")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to enable auto-scaling: {e}")

def start_application():
    """Starts the application on the first available instance in the group."""
    try:
        print("[INFO] Fetching instance from the instance group...")
        get_instance_cmd = [
            "gcloud", "compute", "instance-groups", "list-instances", INSTANCE_GROUP_NAME,
            "--region", REGION, "--format=value(instance)"
        ]
        instance_name = subprocess.check_output(get_instance_cmd, text=True).strip()

        if instance_name:
            print(f"[INFO] Found instance: {instance_name}. Starting application...")
            run_app_cmd = [
                "gcloud", "compute", "ssh", instance_name,
                "--zone", ZONE,
                "--project", PROJECT_ID,
                "--command", f"{APP_COMMAND}"
            ]
            subprocess.run(run_app_cmd, check=True)
            print("[SUCCESS] Application started on instance!")
        else:
            print("[WARNING] No instance found in the group. Skipping app launch.")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to start application: {e}")

def monitor_cpu():
    """Monitors CPU usage and triggers instance group scaling."""
    while True:
        cpu_usage = psutil.cpu_percent(interval=5)
        print(f"[INFO] Current CPU Usage: {cpu_usage}%")

        if cpu_usage > CPU_THRESHOLD_UP:
            print("[ALERT] High CPU detected! Creating Instance Group and Enabling Auto-Scaling...")
            create_instance_group()
            break
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_cpu()
