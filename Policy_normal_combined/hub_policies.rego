package italert_hub_combined

# Returns the list of destinations
# Send to CBE if:
#    "severity": ["extreme", "severe"],
#    "certainty": ["observed", "likely"]
# Otherwise, send to APP and IVR

severity := input.parameters.severity
certainty := input.parameters.certainty

# Seleziona le destinazioni in base alla severity e alla certainty di input
send_to contains dest if {
    destination := data.hub_data.destinations[_]
    severity == destination.severity[_]
    certainty == destination.certainty[_]
    dest := destination.id
}

