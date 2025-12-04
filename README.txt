Docker commands:
- delete all containers: docker rm -vf $(docker ps -aq)
- delete all images: docker rmi -f $(docker images -aq)
- list images: docker image ls 
- list all containers: docker ps -a
- start docker-compose: docker-compose up -d
- verify that servers are listening on the ports:
    nc -zv localhost 22181
    nc -zv localhost 9092

This project is a sample version of the IT-Alert platform for testing access control in paper:
...

Tutorial:
1. Create and run Docker containers:
  $ docker-compose up -d
2. Upload policies and data:
  - Enforcement:
    Ingestor:
      $ curl -X PUT "http://localhost:8181/v1/policies/ingestor/ingestor_policies" -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/ingestor_policies.rego
      $ curl -X PUT http://localhost:8181/v1/data/ingestor_data -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/ingestor_data.json
    Hub:
      $ curl -X PUT "http://localhost:8181/v1/policies/hub/hub_policies" -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/hub_policies.rego
      $ curl -X PUT http://localhost:8181/v1/data/hub_data -H "Content-Type: text/plain" --data-binary @Policy_normal_combined/hub_data.json
  - Risk assessment (Ingestor only):
      $ curl -X PUT "http://localhost:8181/v1/policies/ingestor/ingestor_policies_risk" -H "Content-Type: text/plain" --data-binary @Risk_assessment_combined/ingestor_policies_risk.rego
  - Detection:
      $ curl -X PUT "http://localhost:8181/v1/policies/monitor/hub_policies" -H "Content-Type: text/plain" --data-binary @Policy_detection/hub_policies.rego  
3. Create and start a consumer:
  $ docker-compose exec kafka kafka-console-consumer.sh --topic hub-topic --from-beginning --bootstrap-server kafka:9092
4. To run the experiment, open a new terminal and:
  - Enforcement case:
    1. $ cd Policy_normal_combined
    2. $ python hub.py
    3. On a new terminal: $ python ingestor.py
        Note: to terminate the hub execution, run again python ingestor.py
              final result for the hub will store the first execution time, while for the ingestor the second execution time
  - Detection case:
    1. $ cd Policy_detection
    2. $ python monitor.py
  - Risk Assessment
    1. $ cd Risk_assessment_combined
    2. $ python ingestor.py

