#!/usr/bin/env python3
import json
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ngsi_ld.data_models import spray_pass, spray_session
from orion_client import OrionLDClient


class SprayStatusBridge(Node):
    def __init__(self):
        super().__init__("spray_status_bridge")

        self.declare_parameter("orion_host", "localhost")
        self.declare_parameter("orion_port", 1026)

        orion_host = self.get_parameter("orion_host").value
        orion_port = self.get_parameter("orion_port").value

        self.orion = OrionLDClient(host=orion_host, port=orion_port)

        self.sub = self.create_subscription(
            String,
            "/rapseb/spray_status",
            self.on_spray_status,
            10
        )

    def on_spray_status(self, msg: String):
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().warning("Invalid JSON in spray_status message")
            return

        event_type = payload.get("event_type")

        if event_type == "pass_complete":
            self.handle_pass_complete(payload)
        elif event_type == "session_complete":
            self.handle_session_complete(payload)

    def handle_pass_complete(self, payload: dict):
        try:
            entity = spray_pass(
                pass_id=payload["pass_id"],
                surface_id=payload["surface_id"],
                pass_number=payload["pass_number"],
                coverage_pct=payload["coverage_pct"],
                timestamp=payload.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                duration_s=payload["duration_s"],
                epoxy_g=payload["epoxy_g"],
            )
            if self.orion.upsert(entity):
                self.get_logger().info(f"Upserted SprayPass: {payload['pass_id']}")
            else:
                self.get_logger().warning(f"Failed to upsert SprayPass: {payload['pass_id']}")
        except KeyError as e:
            self.get_logger().warning(f"Missing field in pass_complete: {e}")
        except Exception as e:
            self.get_logger().warning(f"Error pushing SprayPass to Orion: {e}")

    def handle_session_complete(self, payload: dict):
        try:
            entity = spray_session(
                session_id=payload["session_id"],
                surface_id=payload["surface_id"],
                total_passes=payload["total_passes"],
                target_passes=payload["target_passes"],
                final_coverage_pct=payload["final_coverage_pct"],
                total_epoxy_g=payload["total_epoxy_g"],
                start_time=payload.get("start_time", datetime.utcnow().isoformat() + "Z"),
                end_time=payload.get("end_time", datetime.utcnow().isoformat() + "Z"),
                status=payload.get("status", "COMPLETED"),
            )
            if self.orion.upsert(entity):
                self.get_logger().info(f"Upserted SpraySession: {payload['session_id']}")
            else:
                self.get_logger().warning(f"Failed to upsert SpraySession: {payload['session_id']}")
        except KeyError as e:
            self.get_logger().warning(f"Missing field in session_complete: {e}")
        except Exception as e:
            self.get_logger().warning(f"Error pushing SpraySession to Orion: {e}")


def main():
    rclpy.init()
    node = SprayStatusBridge()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
