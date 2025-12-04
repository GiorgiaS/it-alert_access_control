from kafka import KafkaProducer
from opa_client.opa_async import AsyncOpaClient
import asyncio
from myAsyncFunc import my_check_permission
import time
import json

def kafka_write(alert):
    # create a Kafka producer
    # KAFKA_VERSION = (0, 10)
    producer = KafkaProducer(bootstrap_servers='localhost:9093')

    # write to the Hub topic
    topic = 'hub-topic'

    # send data to the topic
    def publish_to_topic(alert):
        producer.send(topic, value=alert)
        producer.flush()
        print(f'Sent alert message: {alert}')

    publish_to_topic(json.dumps(alert).encode('utf-8'))

async def check_authorisation(alert):
    async with AsyncOpaClient(host='localhost', port=8181) as client:
        allow = False
        result = await client.check_connection()
        # print(f'Ingestor::check_authorisation - Connection with OPA remote service: {result}')

        # print(f'Ingestor::check_authorisation  - List of policies: {await client.get_policies_list()}')

        # Evaluate policy
        input_data = alert
        policy_name = 'ingestor/ingestor_policies_risk' # the endpoint = the ID assigned to the policy stored on the OPA service
        rule_name = 'decision' # the value of the variable inside the policy that I want to check

        result = await my_check_permission(
            client,
            input_data=input_data,
            policy_name=policy_name,
            rule_name=rule_name)
        print(f'Ingestor::check_authorisation - Policy assessment result: {result}')
        allow = result['result']['allow']
        return allow
        
async def main():
    alert = {"parameters": {
                "event": "heavy-rain",
                "sender": "rrn",
                "area": "area1",
                "severity": "minor",
                "certainty": "observed"
                }
            }
    allow = await check_authorisation(alert)
    if allow:
        kafka_write(alert)
    else:
        print('Authorisation denied')


with open('./ingestor_risk_assessment_case_combined_time', "w") as f:
    f.write('Execution time for normal case (combined).\nThis time includes the time for querying OPA and for publishing the alert message on the Kafka topic')
tot_time = 0
num_executions = 50
for repetition in range(1, num_executions + 1): # from 1 to 10
    start = time.time()
    asyncio.run(main())
    stop = time.time()
    time_interval = stop - start
    tot_time = tot_time + time_interval
    print('Execution time:', time_interval)
    with open('./ingestor_risk_assessment_case_combined_time', "a") as f:
        f.write('\n' + str(repetition) + '. ' + str(time_interval))
with open('./ingestor_risk_assessment_case_combined_time', "a") as f:
    f.write('\n\n' + 'Number of repetition: ' + str(num_executions))
    f.write('\n' + 'Maximum time: ' + str(tot_time))
    f.write('\n' + 'Average computation time: ' + str(tot_time/num_executions))