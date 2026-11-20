from flask import Flask, render_template, request
from netmiko import ConnectHandler

app = Flask(__name__)


def run_diagnostics():
    router_device = {
        "device_type": "cisco_ios_telnet",
        "ip": "192.168.10.95",
        "port": 32770,
        "username": "admin",
        "password": "eve123",
        "secret": "eve123",
    }
    commands_to_run = [
        "show version",
        "show ip interface brief",
        "show running-config",
    ]

    results = {}
    error = None
    net_connect = None
    phase = "opening the Telnet connection"

    try:
        net_connect = ConnectHandler(**router_device, conn_timeout=20)
        phase = "entering privileged mode"
        net_connect.enable()

        for command in commands_to_run:
            phase = f"running {command!r}"
            results[command] = net_connect.send_command(command, read_timeout=60)
    except Exception as exc:
        error = f"Connection failed while {phase} ({type(exc).__name__}): {exc}"
        app.logger.exception("Router diagnostics failed during %s", phase)
    finally:
        if net_connect is not None:
            try:
                net_connect.disconnect()
            except Exception as exc:
                app.logger.exception("Failed to disconnect from router")
                if error is None:
                    error = f"Disconnect failed ({type(exc).__name__}): {exc}"

    if error is not None:
        raise RuntimeError(error)
    return results


@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    error = None

    if request.method == "POST":
        try:
            results = run_diagnostics()
        except RuntimeError as exc:
            error = str(exc)

    return render_template("index.html", results=results, error=error)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
