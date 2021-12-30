from unittest.mock import MagicMock

from freezegun import freeze_time

from facades import (
    FakeDynamoDBFacadeThatWorksAndHadNoPreviousLoads,
    FakeDynamoDBFacadeThatWorksAndHadPreviousLoads,
    FakeDynamoDBFacadeWithBrokenGetMethod,
    FakeDynamoDBFacadeWithBrokenUpdateMethod,
    FakeFirehoseFacadeBroken,
    FakeFirehoseFacadeWorking,
    FakeMaropostFacadeBroken,
    FakeMaropostFacadeWorking,
)
from facades.logger_facade import LoggerFacade
from main import main


@freeze_time("2012-01-14 03:21:34", tz_offset=0)
def test_get_previous_report_response_is_unavailable():
    magic_mock_for_logger = MagicMock()
    fake_logger = LoggerFacade(magic_mock_for_logger)

    main(
        report_name="Fake Report Name",
        logger=fake_logger,
        dynamo_db_facade=FakeDynamoDBFacadeWithBrokenGetMethod(table="Fake Table"),
        firehose_facade=FakeFirehoseFacadeWorking(),
        maropost_facade=FakeMaropostFacadeWorking(),
    )
    magic_mock_for_logger.error.assert_called_with(
        '{"ERROR": "UNABLE TO GET PREVIOUSLY LOADED Fake Report Name '
        'STATISTICS FROM DYNAMODB.", "ERROR DETAILS": "DynamoDB has been '
        'deprecated. It has been replaced with pen and paper and a telephone number you must call.", '
        '"DATETIME": "2012-01-14 03:21:34+00:00"}'
    )


@freeze_time("2012-01-14 03:21:34", tz_offset=0)
def test_maropost_is_unavailable():
    magic_mock_for_logger = MagicMock()
    fake_logger = LoggerFacade(magic_mock_for_logger)

    main(
        report_name="Fake Report Name",
        logger=fake_logger,
        dynamo_db_facade=FakeDynamoDBFacadeThatWorksAndHadNoPreviousLoads(
            table="Fake Table"
        ),
        firehose_facade=FakeFirehoseFacadeWorking(),
        maropost_facade=FakeMaropostFacadeBroken(),
    )
    magic_mock_for_logger.error.assert_called_with(
        '{"ERROR": "UNABLE TO GET Fake Report Name RESPONSE FROM MAROPOST.", '
        '"ERROR DETAILS": "Maropost is currently on fire. '
        'Please send \\ud83d\\ude92\\ud83d\\ude92\\ud83d\\ude92", '
        '"DATETIME": "2012-01-14 03:21:34+00:00"}'
    )


@freeze_time("2012-01-14 03:21:34", tz_offset=0)
def test_firehose_is_broken():
    magic_mock_for_logger = MagicMock()
    fake_logger = LoggerFacade(magic_mock_for_logger)

    main(
        report_name="Fake Report Name",
        logger=fake_logger,
        dynamo_db_facade=FakeDynamoDBFacadeThatWorksAndHadNoPreviousLoads(
            table="Fake Table"
        ),
        firehose_facade=FakeFirehoseFacadeBroken(),
        maropost_facade=FakeMaropostFacadeWorking(),
    )
    magic_mock_for_logger.error.assert_called_with(
        '{"ERROR": "UNABLE TO LOAD Fake Report Name TO FIREHOSE.", "ERROR DETAILS": "\\ud83e\\udd16 '
        'JEFF BEZOS HAS BLOCKED YOU \\ud83e\\udd16", "PREVIOUS DATA": "{\\"report_name\\": '
        '\\"fake_report_name\\", \\"last_page_loaded\\": 1, '
        '\\"last_item_within_the_page_loaded\\": null}", "DATETIME": "2012-01-14 03:21:34+00:00"}'
    )


@freeze_time("2012-01-14 03:21:34", tz_offset=0)
def test_cant_update_dynamo_db_about_successful_load():
    magic_mock_for_logger = MagicMock()
    fake_logger = LoggerFacade(magic_mock_for_logger)

    main(
        report_name="Fake Report Name",
        logger=fake_logger,
        dynamo_db_facade=FakeDynamoDBFacadeWithBrokenUpdateMethod(table="Fake table"),
        firehose_facade=FakeFirehoseFacadeWorking(),
        maropost_facade=FakeMaropostFacadeWorking(),
    )
    magic_mock_for_logger.error.assert_called_with(
        '{"ERROR": "UNABLE TO UPDATE DYNAMODB ABOUT SUCCESSFUL Fake Report Name LOAD TO FIREHOSE.",'
        ' "ERROR DETAILS": "DynamoDB has been deprecated. It has been replaced with pen and paper and a '
        'telephone number you must call.", "NEW DATA LOADED": {"PAGE_LOADED": 1, "NUMBER_OF_RECORDS": 2}, '
        '"DATETIME": "2012-01-14 03:21:34+00:00"}'
    )


@freeze_time("2012-01-14 03:21:34", tz_offset=0)
def test_successful_load_no_items_loaded_before():
    magic_mock_for_logger = MagicMock()
    fake_logger = LoggerFacade(magic_mock_for_logger)

    main(
        report_name="Fake Report Name",
        logger=fake_logger,
        dynamo_db_facade=FakeDynamoDBFacadeThatWorksAndHadNoPreviousLoads(
            table="Fake table"
        ),
        firehose_facade=FakeFirehoseFacadeWorking(),
        maropost_facade=FakeMaropostFacadeWorking(),
    )

    magic_mock_for_logger.info.assert_called_with(
        '{"SUCCESS": "SUCCESSFULLY LOADED DATA.", "NEW DATA LOADED": {"PAGE_LOADED": 1, "NUMBER_OF_RECORDS": 2}, '
        '"DATETIME": "2012-01-14 03:21:34+00:00"}'
    )


@freeze_time("2012-01-14 03:21:34", tz_offset=0)
def test_successful_load_new_page():
    magic_mock_for_logger = MagicMock()
    fake_logger = LoggerFacade(magic_mock_for_logger)

    main(
        report_name="Fake Report Name",
        logger=fake_logger,
        dynamo_db_facade=FakeDynamoDBFacadeThatWorksAndHadPreviousLoads(
            table="Blah blah"
        ),
        firehose_facade=FakeFirehoseFacadeWorking(),
        maropost_facade=FakeMaropostFacadeWorking(),
    )

    magic_mock_for_logger.info.assert_called_with(
        '{"SUCCESS": "SUCCESSFULLY LOADED DATA.", "NEW DATA LOADED": {"PAGE_LOADED": 4, "NUMBER_OF_RECORDS": 2}, '
        '"DATETIME": "2012-01-14 03:21:34+00:00"}'
    )
