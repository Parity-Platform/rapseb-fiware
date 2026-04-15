CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"


def spray_pass(
    pass_id: str,
    surface_id: str,
    pass_number: int,
    coverage_pct: float,
    timestamp: str,
    duration_s: float,
    epoxy_g: float,
) -> dict:
    return {
        "@context": CONTEXT,
        "id": f"urn:ngsi-ld:SprayPass:{pass_id}",
        "type": "SprayPass",
        "passId": {"type": "Property", "value": pass_id},
        "surfaceId": {"type": "Property", "value": surface_id},
        "passNumber": {"type": "Property", "value": pass_number},
        "coveragePercentage": {"type": "Property", "value": coverage_pct},
        "timestamp": {"type": "Property", "value": timestamp},
        "duration": {"type": "Property", "value": duration_s, "unitCode": "SEC"},
        "epoxyUsed": {"type": "Property", "value": epoxy_g, "unitCode": "GRM"},
    }


def spray_session(
    session_id: str,
    surface_id: str,
    total_passes: int,
    target_passes: int,
    final_coverage_pct: float,
    total_epoxy_g: float,
    start_time: str,
    end_time: str,
    status: str,
) -> dict:
    return {
        "@context": CONTEXT,
        "id": f"urn:ngsi-ld:SpraySession:{session_id}",
        "type": "SpraySession",
        "sessionId": {"type": "Property", "value": session_id},
        "surfaceId": {"type": "Property", "value": surface_id},
        "totalPasses": {"type": "Property", "value": total_passes},
        "targetPasses": {"type": "Property", "value": target_passes},
        "finalCoveragePercentage": {"type": "Property", "value": final_coverage_pct},
        "totalEpoxyUsed": {"type": "Property", "value": total_epoxy_g, "unitCode": "GRM"},
        "startTime": {"type": "Property", "value": start_time},
        "endTime": {"type": "Property", "value": end_time},
        "status": {"type": "Property", "value": status},
    }
