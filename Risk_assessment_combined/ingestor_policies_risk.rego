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
default p_a_fn := 0.3
default p_a_fp := 0.6
default i_h := 7
default i_f := 4
default efficacy := 0.8
default trust := 0.6
default plausibility := 0.3
default ioc := 0.8
default r_u := 100
default expected_risk_fn := 0
default expected_risk_fp := 0
default x := 100
default y := 0
default risk_assessment_fn := "don't"
default risk_assessment_fp := "don't"

r_u := x if {
    x := p_h * i_h
}

# Assess False Negative
expected_risk_fn := y if {
    rr := p_h * i_h * efficacy
    r_m := p_h * i_h - rr
    y := p_a_fn * r_u + (1 - p_a_fn) * r_m + (1 - p_h) * i_f 
}
risk_assessment_fn := "send" if {
    expected_risk_fn < r_u
} 

# Assess False Positive
expected_risk_fp := y if {
    rr := p_h * i_h * efficacy
    r_m := p_h * i_h - rr
    y := p_a_fp * r_u + (1- p_a_fp) * r_m + (1-p_h) * i_f 
}
risk_assessment_fp := "send" if {
    expected_risk_fp < r_u
} 

allow if {
    event in allowed_alert_type_from_sender
    event in allowed_alert_type_from_area
}

decision := {
    "allow": allow,
    "R_U": r_u,
    "expected_risk_fn": expected_risk_fn, 
    "risk_assessment_fn": risk_assessment_fn,
    "expected_risk_fp": expected_risk_fp, 
    "risk_assessment_fp": risk_assessment_fp
}
