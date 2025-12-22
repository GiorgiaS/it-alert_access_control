package italert_ingestor_risk

# Allow if:
# - the alert type is within a geospatial code;
# - the sender can send the alert type

default allow = false
event := input.parameters.event
sender := input.parameters.sender
area := input.parameters.area
allowed_alert_type_from_sender := data.ingestor_data.allowed_alert_type_from_sender[sender]
allowed_alert_type_from_area := data.ingestor_data.allowed_alert_type_from_area[area]

default safety_risk = 100
default security_risk = 100

# Sender risk
default sender_w = 0.7
default sender_max = 3
risk_sender := 3 if sender == "uds"
risk_sender := 2 if sender == "rrn"
risk_sender := 1 if sender == "cbe"

# Event risk (mountain area)
default event_w = 0.3
default event_max = 4
risk_event := 4 if event == "tsunami"
risk_event := 3 if event == "nuclear"
risk_event := 2 if event == "industrial"
risk_event := 1 if event == "heavy-rain"

# Safety risk parameters
default p_ev := 0.75
default i_ev = 6
default i_fa := 2
default ef := 0.8

# Assess security risk
security_risk := x if {
    x := sender_w*(risk_sender/sender_max)+event_w*(risk_event/event_max)
}

safety_risk := x if {
        x := (1-p_ev)*i_fa*security_risk+(p_ev*i_ev*(1-ef)+(1-p_ev)*i_fa)*(1-security_risk)
        }

allow if {
    event in allowed_alert_type_from_sender
    event in allowed_alert_type_from_area
}

decision := {
    "allow": allow,
    "safety_risk": safety_risk, 
    "security_risk": security_risk, 
}
