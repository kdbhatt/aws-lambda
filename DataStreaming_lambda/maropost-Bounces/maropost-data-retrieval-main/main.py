import json
import time
import arrow
import boto3
import os
import boto3.dynamodb.table
import requests
from mypy_boto3_firehose import FirehoseClient

from facades.dynamodb_facade import AbstractDynamoDBFacade, DynamoDBFacade
from facades.firehose_facade import AbstractFirehoseFacade, FirehoseFacade
from facades.logger_facade import LoggerFacade
from facades.maropost_facade import AbstractMaropostFacade, MaropostFacade
from facades.table_facade import TableFacade
from logger_factory import get_logger
from settings import (
    AUTH_TOKEN,
    ENDPOINT_URL,
    LOG_GROUP,
    REGION_NAME,
    REPORT_NAME,
    TABLE_NAME,
    STREAM_NAME,
)


def main(
    report_name: str,
    logger: LoggerFacade,
    dynamo_db_facade: AbstractDynamoDBFacade,
    firehose_facade: AbstractFirehoseFacade,
    maropost_facade: AbstractMaropostFacade,
):
    #print('1- start' + arrow.now().to("utc").format(arrow.FORMAT_W3C))
    previous_successful_load_response = (
        dynamo_db_facade.get_if_previous_load_was_successful(report_name)
    )
    if previous_successful_load_response.success_status is False:
        logger.error(
            json.dumps(
                {
                    "ERROR": f"UNABLE TO GET PREVIOUSLY LOADED {report_name} STATISTICS FROM DYNAMODB.",
                    "ERROR DETAILS": previous_successful_load_response.error,
                    "DATETIME": arrow.now().to("utc").format(arrow.FORMAT_W3C),
                }
            )
        )
        return
    #print('2- call dynamo' + arrow.now().to("utc").format(arrow.FORMAT_W3C))
    api_response = maropost_facade.get_page_of_data(
        previous_successful_load_response.data.page_to_load
    )
    if api_response.success_status is False:
        logger.error(
            json.dumps(
                {
                    "ERROR": f"UNABLE TO GET {report_name} RESPONSE FROM MAROPOST.",
                    "ERROR DETAILS": api_response.error,
                    "DATETIME": arrow.now().to("utc").format(arrow.FORMAT_W3C),
                }
            )
        )
        return

    # api_response.data = api_response.data.get('campaigns','')
    #print('3- api call' + arrow.now().to("utc").format(arrow.FORMAT_W3C))
    if len(api_response.data) <= previous_successful_load_response.data.item_to_start_loading_from:
        logger.info(
            json.dumps(
                {
                    "SUCCESS": "NO NEW DATA TO LOAD",
                    "NEW DATA LOADED": {
                        "PAGE_LOADED": previous_successful_load_response.data.page_to_load,
                        "NUMBER_OF_RECORDS": 0,
                    },
                    "DATETIME": arrow.now().to("utc").format(arrow.FORMAT_W3C),
                }
            )
        )
        return

    firehose_response = firehose_facade.load_data(
        stream_name=STREAM_NAME,
        data=api_response.data[
            previous_successful_load_response.data.item_to_start_loading_from :
        ],
    )
    if firehose_response.success_status is False:
        logger.error(
            json.dumps(
                {
                    "ERROR": f"UNABLE TO LOAD {report_name} TO FIREHOSE.",
                    "ERROR DETAILS": firehose_response.error,
                    "PREVIOUS DATA": str(previous_successful_load_response.data),
                    "DATETIME": arrow.now().to("utc").format(arrow.FORMAT_W3C),
                }
            )
        )
        return
    #print('4- firehose' + arrow.now().to("utc").format(arrow.FORMAT_W3C))
    dynamo_db_response = dynamo_db_facade.update_dynamo_db_about_successful_load(
        report_name=report_name,
        page_loaded=previous_successful_load_response.data.page_to_load,
        last_item_index_loaded=len(api_response.data) - 1,
    )
    if dynamo_db_response.success_status is False:
        logger.error(
            json.dumps(
                {
                    "ERROR": f"UNABLE TO UPDATE DYNAMODB ABOUT SUCCESSFUL {report_name} LOAD TO FIREHOSE.",
                    "ERROR DETAILS": dynamo_db_response.error,
                    "NEW DATA LOADED": {
                        "PAGE_LOADED": previous_successful_load_response.data.page_to_load,
                        "NUMBER_OF_RECORDS": len(
                            api_response.data[
                                previous_successful_load_response.data.item_to_start_loading_from :
                            ]
                        ),
                    },
                    "DATETIME": arrow.now().to("utc").format(arrow.FORMAT_W3C),
                }
            )
        )
        return
    #print('5- dynamo update' + arrow.now().to("utc").format(arrow.FORMAT_W3C))
    logger.info(
        json.dumps(
            {
                "SUCCESS": "SUCCESSFULLY LOADED DATA.",
                "NEW DATA LOADED": {
                    "PAGE_LOADED": previous_successful_load_response.data.page_to_load,
                    "NUMBER_OF_RECORDS": len(
                        api_response.data[
                            previous_successful_load_response.data.item_to_start_loading_from :
                        ]
                    ),
                },
                "DATETIME": arrow.now().to("utc").format(arrow.FORMAT_W3C),
            }
        )
    )

    #print('6- end' + arrow.now().to("utc").format(arrow.FORMAT_W3C))

if __name__ == "__main__":
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    logger = get_logger(LOG_GROUP)

    dynamodb_table: TableFacade = TableFacade(
        boto3.resource("dynamodb", region_name=REGION_NAME).Table(TABLE_NAME)
    )
    firehose_client: FirehoseClient = boto3.client("firehose")

    dynamo_db_facade = DynamoDBFacade(dynamodb_table)
    firehose_facade = FirehoseFacade(firehose_client)
    maropost_facade = MaropostFacade(
        auth_token=AUTH_TOKEN,
        endpoint_url=ENDPOINT_URL,
        requests=requests,
    )

    # With limit of 500 records in Putrecords, looping 10 times to get 5000 records at one run
    for x in range(0, 5000):
        main(REPORT_NAME, logger, dynamo_db_facade, firehose_facade, maropost_facade)
        # time.sleep(2)
        # if (x % 20) == 0:
        #     time.sleep(60)
else:
    pass
