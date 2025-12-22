This project is a sample version of the IT-Alert platform for testing access control in paper:
Risk-based Authorization in Safety Critical Microservice Architectures.
```
Paper under review
```

## Requirements
- Python 3.13+[^1]
- Docker Compose[^2]

## Overview
This project is composed of two folders:
- `Policy_normal_combined`: it includes the file to assess Rego-defined policies for the Hub and the Ingestor.
- `Risk_assessment_combined`: it includes the file to assess Rego-defined risk assessment policies for the Ingestor.

## Tutorial
First of all, run Docker compose commands to initiate the system from inside `it-alert_access_control` folder.
```bash
docker-compose up -d
```
### Policy_normal_combined
Enter `it-alert_access_control` folder and execute the following commands on the terminal:
```bash
curl -X PUT "http://localhost:8181/v1/policies/ingestor/ingestor_policies" -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/ingestor_policies.rego
```
```bash
curl -X PUT http://localhost:8181/v1/data/ingestor_data -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/ingestor_data.json
```
```bash
curl -X PUT "http://localhost:8181/v1/policies/hub/hub_policies" -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/hub_policies.rego
```
```bash
curl -X PUT http://localhost:8181/v1/data/hub_data -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/hub_data.json
```
Optional: on a separate terminal create a Kafka consumer:
```bash
docker-compose exec kafka kafka-console-consumer.sh --topic hub-topic --from-beginning --bootstrap-server kafka:9092
```
Enter `Policy_normal_combined` folder and execute: 
```bash
python hub.py
```
and then
```bash
python ingestor.py
```
To properly terminate the Hub execution, run again the Ingestor script.

### Risk_assessment_combined
Enter `it-alert_access_control` folder and execute the following commands on the terminal:
```bash
curl -X PUT "http://localhost:8181/v1/policies/ingestor/ingestor_policies_risk" -H "Content-Type: text/plain" --data-binary @Risk_assessment_combined/ingestor_policies_risk.rego
```
Execute the Ingestor:
```bash
python ingestor.py
```


[^1]: https://www.python.org/
[^2]: https://docs.docker.com/compose/
