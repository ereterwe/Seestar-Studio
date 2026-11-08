"""Explicit read-only real-hardware acceptance probe. No raw RPC logging."""
import argparse
import json
import time
from pathlib import Path
from telescope_desk.manager import TelescopeManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--output", default="reports/hardware.json")
    parser.add_argument("--exercise-reconnect", action="store_true")
    args = parser.parse_args()
    manager = TelescopeManager()
    observations = {}
    lifecycle = []
    paused_sn = None
    resume_at = None
    resumed_at = None
    manager.start()
    try:
        end = time.monotonic() + args.seconds
        while time.monotonic() < end:
            values, message = manager.latest()
            ready = [sn for sn, (_, tel, frame) in values.items() if tel.connected and frame]
            if args.exercise_reconnect and paused_sn is None and len(ready) >= 2:
                paused_sn = sorted(ready)[0]
                manager.set_paused(paused_sn, True)
                lifecycle.append({"action": "disconnect_requested", "serial": paused_sn, "at": time.time()})
                resume_at = time.monotonic() + 12
            if resume_at and time.monotonic() >= resume_at:
                manager.set_paused(paused_sn, False)
                lifecycle.append({"action": "reconnect_requested", "serial": paused_sn, "at": time.time()})
                resumed_at = time.time()
                resume_at = None
            for sn, (info, telemetry, frame) in values.items():
                record = observations.setdefault(sn, {"model": info.model, "connected_seen": False, "frames": [], "telemetry": {}})
                record["connected_seen"] |= telemetry.connected
                record["telemetry"] = telemetry.values
                if sn == paused_sn and telemetry.paused and not any(x["action"] == "disconnect_observed" for x in lifecycle):
                    lifecycle.append({"action": "disconnect_observed", "at": time.time()})
                if sn == paused_sn and resumed_at and frame and frame.received_at > resumed_at and not any(x["action"] == "new_frame_after_reconnect" for x in lifecycle):
                    lifecycle.append({"action": "new_frame_after_reconnect", "at": time.time()})
                if frame and not any(f["received_at"] == frame.received_at for f in record["frames"]):
                    record["frames"].append({"sequence": frame.sequence, "received_at": frame.received_at,
                        "kind": frame.kind, "format": frame.source_format,
                        "width": frame.image.width(), "height": frame.image.height()})
                    print(f"{sn}: {frame.kind} {frame.source_format} #{frame.sequence}", flush=True)
            time.sleep(1)
    finally:
        manager.stop()
        manager.join(40)
    report = {"test_type": "real hardware, read-only", "duration_s": args.seconds,
              "shutdown_complete": not manager.running, "devices": observations, "lifecycle": lifecycle}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report: {path}; devices: {len(observations)}; shutdown: {not manager.running}")


if __name__ == "__main__":
    main()
