package italert_monitor

# Allow if:
# - the alert type is within a geospatial code;
# - the sender can send the alert type

default allow = false
event := input.parameters.event
sender := input.parameters.sender
area := input.parameters.area
allowed_alert_type_from_sender := data.ingestor_data.allowed_alert_type_from_sender[sender]
allowed_alert_type_from_area := data.ingestor_data.allowed_alert_type_from_area[area]


allow if {
    event in allowed_alert_type_from_sender
    event in allowed_alert_type_from_area
}
