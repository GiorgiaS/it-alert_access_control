from kafka import KafkaConsumer, TopicPartition
from opa_client.opa_async import AsyncOpaClient
import asyncio
from myAsyncFunc import my_check_permission
import time
import json

# Reads from the Hub topic and then decides where to transmit it (e.g., IVR and/or app and/or CBE)
async def kafka_read():
    # read from topic
    topic = 'hub-topic'
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9093',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
    )

    print("Waiting for alerts...")
    # consumer.subscribe(topics=['hub-topic'])
    partition = TopicPartition(topic, 0)
    end_offset = consumer.end_offsets([partition])
    consumer.seek(partition, list(end_offset.values())[0])

    tot_time = 0

    num_executions = 50 # it must be the number of published messages of the ingestor + 1 to close the hub execution and get the resultimg computational time
    repetition = 1
    for msg in consumer:
        # Limit the authorisation assessment to a number of published messages
        if repetition <= num_executions:
            try:
                start = time.time()

                # Take the alert from the message on the topic
                alert = json.loads(msg.value.decode('utf-8'))
                print('Alet message:', alert)
                
                send_to = await check_authorisation(alert)
                print('Query result:', send_to, '\n')

                stop = time.time()
                time_interval = stop - start
                tot_time = tot_time + time_interval
                # print('Execution time for authorisation assessment:', time_interval)
                
                with open('hub_normal_case_combined_time', "a") as f:
                    f.write('\n' + str(repetition) + '. ' + str(time_interval))
                
                repetition = repetition + 1

            except Exception as e:
                print('Not an alert\n')
                print(f"JSON parsing error: {e}\n")
        else:
            consumer.close()
            break

    with open('hub_normal_case_combined_time', "a") as f:
        f.write('\n\n' + 'Number of repetition: ' + str(num_executions))
        f.write('\n' + 'Maximum time: ' + str(tot_time))
        f.write('\n' + 'Average computation time: ' + str(tot_time/num_executions))


async def check_authorisation(alert):
    async with AsyncOpaClient(host='localhost', port=8181) as client:
        send_to = []
        result = await client.check_connection()
        # print(f'Spooler::main - Connection with OPA remote service: {result}')

        # print(f'Spooler::main - List of policies: {await client.get_policies_list()}')

        # Evaluate policy
        input_data = alert
        policy_name = 'hub/hub_policies' # the endpoint = the ID assigned to the policy stored on the OPA service
        rule_name = 'send_to' # the value of the variable inside the policy that I want to check

        result = await my_check_permission(
            client,
            input_data=input_data,
            policy_name=policy_name,
            rule_name=rule_name)
        # print(f'Hub::main - Policy assessment result: {result}')
        send_to = result['result']
        return send_to


with open('hub_normal_case_combined_time', "w") as f:
    f.write('Execution time for detection case.\nThis time includes the time for reading the alert on Kafka topic and the interaction with OPA to assess the authorisation')
asyncio.run(kafka_read())