import argparse
import datetime
import json
import random
import time
import uuid

import confluent_kafka

import config
import model
import util


def main():
    args = parse_args()
    generate_transactions(args[0])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--producer-name', nargs='*', default=["producer_{}".format(random.randint(0, 10000))])
    args = parser.parse_args()
    producer_name = args.producer_name[0]

    return producer_name,


def generate_transactions(producer_name, accounts_count=100, min_value=0, max_value=100):
    producer_conf = {'bootstrap.servers': config.get_str_value(config.KAFKA_PRODUCER_BOOTSTRAP_SERVERS),
                     'client.id': producer_name}

    producer = confluent_kafka.Producer(producer_conf)

    start_time = time.time()
    count = 0
    try:
        while True:
            transaction_uuid = uuid.uuid4()
            src_account_id = random.randint(0, accounts_count)
            dst_account_id = random.randint(0, accounts_count)
            while src_account_id == dst_account_id:
                dst_account_id = random.randint(0, accounts_count)
            amount = round(random.uniform(min_value, max_value), 2)
            timestamp = datetime.datetime.now().isoformat()
            transaction = model.Transaction(transaction_uuid, src_account_id, dst_account_id, amount, timestamp)
            transaction_json = json.dumps(transaction.__dict__, cls=util.JsonEncoder)

            print("producer={}\ttransaction={}".format(producer_name, transaction_json))

            producer.produce(config.get_str_value(config.KAFKA_TOPIC_NAME), key=str(transaction.transaction_id),
                             value=transaction_json)
            producer.flush()

            count += 1

    except KeyboardInterrupt:
        print("Terminated execution")
        pass

    finally:
        passed_time = time.time() - start_time
        print("Execution time: {}s".format(round(passed_time)))
        print("Transactions created: {}".format(count))
        print("Transactions creation rate: {} trans/s".format(round(count / passed_time, 2)))


main()