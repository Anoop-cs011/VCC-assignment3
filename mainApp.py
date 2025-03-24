from flask import Flask, render_template, make_response
import threading
import multiprocessing
import socket

app = Flask(__name__)
running = False
workers = []

def cpu_stress():
    """Function to perform CPU-intensive work."""
    while running:
        # Heavy computation 
        limit = 10**7  # Adjust this for more CPU load
        primes = [True] * (limit + 1)
        primes[0] = primes[1] = False
        for num in range(2, int(limit ** 0.5) + 1):
            if primes[num]:
                for multiple in range(num * num, limit + 1, num):
                    primes[multiple] = False
        result = []
        for num, is_prime in enumerate(primes):
            if is_prime:
                result.append(num)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1)) # random unreachable IP
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def index():
    global running
    return render_template(
        "index.html",
        working= running
    )

@app.route("/start")
def start_stress():
    """Start CPU-intensive work."""
    global running, workers
    running = True
    num_cores = max(multiprocessing.cpu_count()*4, 16)

    for _ in range(num_cores):
        t = threading.Thread(target=cpu_stress)
        workers.append(t)
        t.start()

    # return "CPU stress test started", 200
    template = render_template(
        "index.html",
        working= running
    )
    response = make_response(template, 302)
    response.headers["Location"] = "/"
    return response

@app.route("/stop")
def stop_stress():
    """Stop CPU-intensive work."""
    global running
    running = False

    # return "CPU stress test stopped", 200
    template = render_template(
        "index.html",
        working= running
    )
    response = make_response(template, 302)
    response.headers["Location"] = "/"
    return response

if __name__ == "__main__":
    app.run(host= get_ip(), port=8080)
