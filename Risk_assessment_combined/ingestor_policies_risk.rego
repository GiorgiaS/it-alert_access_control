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

# Risk assessment
default p_h = 0.8
default p_a = 0.3
default i_h = 7
default i_f = 4
default efficacy = 0.8
default trust = 0.6
default plausibility = 0.3
default ioc = 0.8
default risk_assessment := ""


# Assess security risk
no_message_risk := x if {
    x := p_a * p_h * i_h
}

message_risk:= x if {
        r_m = p_h * i_h * (1-efficacy) - (1-p_h) * i_f
        x := (1-p_a) * r_m
        }

risk_assessment := "send" if {
    no_message_risk > message_risk
} else := "not send"

allow if {
    event in allowed_alert_type_from_sender
    event in allowed_alert_type_from_area
}

decision := {
    "allow": allow,
    "no_message_risk": no_message_risk, 
    "message_risk": message_risk, 
    "risk_assessment": risk_assessment
}
