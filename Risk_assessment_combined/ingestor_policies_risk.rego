package italert_ingestor_risk

# Allow if:
# - the alert type is within a geospatial code;
# - the sender can send the alert type

default allow := false
event := input.parameters.event
sender := input.parameters.sender
area := input.parameters.area
allowed_alert_type_from_sender := data.ingestor_data.allowed_alert_type_from_sender[sender]
allowed_alert_type_from_area := data.ingestor_data.allowed_alert_type_from_area[area]

# Risk assessment
default p_h := 0.8
default p_a := 0.3
default i_h := 7
default i_f := 4
default efficacy := 0.8
default trust := 0.6
default plausibility := 0.3
default ioc := 0.8
default risk_assessment_fn := "not send"
default risk_assessment_fp := "not send"


# Assess False Negative
no_message_risk_fn := x if {
    x := p_a * p_h * i_h
}

message_risk_fn:= x if {
        r_m = p_h * i_h * (1-efficacy) - (1-p_h) * i_f
        x := (1-p_a) * r_m
        }

risk_assessment_fn := "send" if {
    no_message_risk_fn > message_risk_fn
} 
# Assess False Positive
no_message_risk_fp := x if {
    x := (1-p_a) * p_h * i_h
}

message_risk_fp:= x if {
        r_m = p_h * i_h * (1-efficacy) - (1-p_h) * i_f
        x := (p_a) * r_m
        }

risk_assessment_fn := "send" if {
    no_message_risk_fn > message_risk_fp
}

allow if {
    event in allowed_alert_type_from_sender
    event in allowed_alert_type_from_area
}

decision := {
    "allow": allow,
    "no_message_risk_fn": no_message_risk_fn, 
    "message_risk_fn": message_risk_fn, 
    "risk_assessment_fn": risk_assessment_fn,
    "no_message_risk_fp": no_message_risk_fp, 
    "message_risk_fp": message_risk_fp, 
    "risk_assessment_fp": risk_assessment_fp
}
