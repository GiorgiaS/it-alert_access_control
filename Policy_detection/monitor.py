from kafka import KafkaConsumer
from opa_client.opa_async import AsyncOpaClient
import asyncio
from myAsyncFunc import my_check_permission
import time
import json

async def kafka_read():
    # topic
    topic = 'hub-topic'
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9093',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
    )

    print("Waiting for alerts...")
    tot_time = 0
    num_executions = 50
    repetition = 1
    for msg in consumer:
        # Limit the authorisation assessment to a number of published messages
        if repetition <= num_executions:
            try:
                start = time.time()

                # Take the alert from the message on the topic
                alert = json.loads(msg.value.decode('utf-8'))
                # print(alert)
                
                allow = await check_authorisation(alert)
                print('Query result:', allow, '\n')

                stop = time.time()
                time_interval = stop - start
                tot_time = tot_time + time_interval
                print('Execution time for authorisation assessment:', time_interval)
                
                with open('detection_case_time', "a") as f:
                    f.write('\n' + str(repetition) + '. ' + str(time_interval))
                
                repetition = repetition + 1

            except Exception as e:
                print('Not an alert\n')
                print(f"JSON parsing error: {e}\n")
        else:
            break

    with open('detection_case_time', "a") as f:
        f.write('\n\n' + 'Number of repetition: ' + str(num_executions))
        f.write('\n' + 'Maximum time: ' + str(tot_time))
        f.write('\n' + 'Average computation time: ' + str(tot_time/num_executions))





async def check_authorisation(alert):
    async with AsyncOpaClient(host='localhost', port=8181) as client:
        allow = False
        result = await client.check_connection()
        # print(f'Spooler::main - Connection with OPA remote service: {result}')

        # print(f'Spooler::main - List of policies: {await client.get_policies_list()}')

        # Evaluate policy
        input_data = alert
        policy_name = 'monitor/hub_policies' # the endpoint = the ID assigned to the policy stored on the OPA service
        rule_name = 'allow' # the value of the variable inside the policy that I want to check

        result = await my_check_permission(
            client,
            input_data=input_data,
            policy_name=policy_name,
            rule_name=rule_name)
        print(f'Spooler::main - Policy assessment result: {result}')
        allow = result['result']
        return allow


with open('detection_case_time', "w") as f:
    f.write('Execution time for detection case.\nThis time includes the time for reading the alert on Kafka topic and the interaction with OPA to assess the authorisation')
asyncio.run(kafka_read())