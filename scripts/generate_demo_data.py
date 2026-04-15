#!/usr/bin/env python3
"""RAPSEB demo data: UR10e epoxy spraying on 30x30 cm biocomposite boards."""

import csv, json, os, random
from datetime import datetime, timedelta

random.seed(2023)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# 3 demo days, ~12 boards/day
DAY_STARTS = [
    datetime(2026, 3, 16, 9, 0),
    datetime(2026, 3, 17, 9, 15),
    datetime(2026, 3, 18, 8, 45),
]
BOARDS_PER_DAY = [12, 14, 12]


def generate_sessions():
    sessions = []
    board_num = 0
    for day_idx, day_start in enumerate(DAY_STARTS):
        t = day_start
        for _ in range(BOARDS_PER_DAY[day_idx]):
            board_num += 1
            abort = random.random() < 0.03  # ~1 abort in 38 boards
            target = random.choice([3, 3, 3, 4])  # mostly 3 passes
            actual = 1 if abort else target

            if abort:
                cov = random.uniform(38, 52)
                epoxy = random.uniform(1.1, 1.6)
                dur = random.uniform(6, 10)
            else:
                cov = random.uniform(96.5, 99.4)
                epoxy = random.uniform(4.1, 5.0)
                dur = random.uniform(21, 27)

            end = t + timedelta(seconds=dur)
            sessions.append({
                "session_id": f"session-{board_num:03d}",
                "surface_id": f"board-{board_num:03d}",
                "total_passes": actual,
                "target_passes": target,
                "final_coverage_pct": round(cov, 1),
                "total_epoxy_g": round(epoxy, 2),
                "start_time": t.isoformat() + "Z",
                "end_time": end.isoformat() + "Z",
                "status": "aborted" if abort else "completed",
                "duration_s": round(dur, 1),
            })
            # gap between boards: 4-8 min, occasional longer break
            gap = random.uniform(240, 480)
            if random.random() < 0.08:
                gap += random.uniform(600, 1800)  # lunch / recalibration
            t = end + timedelta(seconds=gap)
    return sessions


def generate_passes(sessions):
    passes = []
    n = 0
    for s in sessions:
        t0 = datetime.fromisoformat(s["start_time"].replace("Z", ""))
        dt = s["duration_s"] / s["total_passes"]
        for p in range(1, s["total_passes"] + 1):
            n += 1
            if s["status"] == "aborted":
                cov = random.uniform(38, 52)
            else:
                cov = {1: random.uniform(42, 58),
                       2: random.uniform(74, 85),
                       3: random.uniform(93, 98),
                       4: random.uniform(97, 99.4)}.get(p, random.uniform(97, 99))
            ep = s["total_epoxy_g"] / s["total_passes"] + random.uniform(-0.08, 0.08)
            passes.append({
                "pass_id": f"pass-{n:05d}",
                "session_id": s["session_id"],
                "surface_id": s["surface_id"],
                "pass_number": p,
                "coverage_pct": round(cov, 1),
                "timestamp": (t0 + timedelta(seconds=(p - 0.5) * dt)).isoformat() + "Z",
                "duration_s": round(dt, 1),
                "epoxy_g": round(max(0.9, ep), 2),
            })
    return passes


def to_ngsi(items, entity_type, id_field):
    ctx = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
    return [{"@context": ctx,
             "id": f"urn:ngsi-ld:{entity_type}:{i[id_field]}",
             "type": entity_type,
             **{k: {"type": "Property", "value": v} for k, v in i.items()}}
            for i in items]


def write_csv(name, rows):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def write_json(name, data):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  {name}: {len(data)} entities")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sessions = generate_sessions()
    passes = generate_passes(sessions)

    write_csv("spraying_sessions.csv", sessions)
    write_csv("spray_passes.csv", passes)
    write_json("spraying_sessions.json", to_ngsi(sessions, "SpraySession", "session_id"))
    write_json("spray_passes.json", to_ngsi(passes, "SprayPass", "pass_id"))

    done = [s for s in sessions if s["status"] == "completed"]
    aborted = len(sessions) - len(done)
    avg_cov = sum(s["final_coverage_pct"] for s in done) / len(done)
    avg_ep = sum(s["total_epoxy_g"] for s in done) / len(done)
    print(f"\n  {len(sessions)} boards, {aborted} aborted")
    print(f"  Avg coverage (completed): {avg_cov:.1f}%")
    print(f"  Avg epoxy (completed): {avg_ep:.2f} g")


if __name__ == "__main__":
    main()
