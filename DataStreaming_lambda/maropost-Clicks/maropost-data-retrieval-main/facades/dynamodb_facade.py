from abc import ABCMeta, abstractmethod

from adapters import ReportResponseDynamodbAdapter
from facades.table_facade import TableFacade
from model import ExternalResourceResponse


class AbstractDynamoDBFacade(object, metaclass=ABCMeta):
    @abstractmethod
    def get_if_previous_load_was_successful(
        self, report_name: str
    ) -> ExternalResourceResponse:
        pass

    @abstractmethod
    def update_dynamo_db_about_successful_load(
        self, report_name: str, page_loaded: int, last_item_index_loaded: int
    ) -> ExternalResourceResponse:
        pass


class FakeDynamoDBFacadeWithBrokenGetMethod(AbstractDynamoDBFacade):
    def __init__(self, table: TableFacade):
        self._table = table

    def get_if_previous_load_was_successful(
        self, report_name: str
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=False,
            data=None,
            error="DynamoDB has been deprecated. It has been replaced with pen and paper and a telephone number"
            " you must call.",
        )

    def update_dynamo_db_about_successful_load(
        self, report_name: str, page_loaded: int, last_item_index_loaded: int
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(success_status=True, data=None, error=None)


class FakeDynamoDBFacadeWithBrokenUpdateMethod(AbstractDynamoDBFacade):
    def __init__(self, table: TableFacade):
        self._table = table

    def get_if_previous_load_was_successful(
        self, report_name: str
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=True,
            data=ReportResponseDynamodbAdapter(
                {
                    "Item": {
                        "report_name": "fake_report_name",
                        "last_page_loaded": 1,
                        "last_item_within_the_page_loaded": None,
                    }
                }
            ),
            error=None,
        )

    def update_dynamo_db_about_successful_load(
        self, report_name: str, page_loaded: int, last_item_index_loaded: int
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=False,
            data=None,
            error="DynamoDB has been deprecated. It has been replaced with pen and paper and a "
            "telephone number you must call.",
        )


class FakeDynamoDBFacadeThatWorksAndHadNoPreviousLoads(AbstractDynamoDBFacade):
    def __init__(self, table: TableFacade):
        self._table = table

    def get_if_previous_load_was_successful(
        self, report_name: str
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=True,
            data=ReportResponseDynamodbAdapter(
                {
                    "Item": {
                        "report_name": "fake_report_name",
                        "last_page_loaded": 1,
                        "last_item_within_the_page_loaded": None,
                    }
                }
            ),
            error=None,
        )

    def update_dynamo_db_about_successful_load(
        self, report_name: str, page_loaded: int, last_item_index_loaded: int
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(success_status=True, data=None, error=None)


class FakeDynamoDBFacadeThatWorksAndHadPreviousLoads(AbstractDynamoDBFacade):
    def __init__(self, table: TableFacade):
        self._table = table

    def get_if_previous_load_was_successful(
        self, report_name: str
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=True,
            data=ReportResponseDynamodbAdapter(
                {
                    "Item": {
                        "report_name": "fake_report_name",
                        "last_page_loaded": 3,
                        "last_item_within_the_page_loaded": 199,
                    }
                }
            ),
            error=None,
        )

    def update_dynamo_db_about_successful_load(
        self, report_name: str, page_loaded: int, last_item_index_loaded: int
    ) -> ExternalResourceResponse:
        return ExternalResourceResponse(success_status=True, data=None, error=None)


class DynamoDBFacade(AbstractDynamoDBFacade):
    def __init__(self, table: TableFacade):
        self._table = table

    def get_if_previous_load_was_successful(
        self, report_name: str
    ) -> ExternalResourceResponse:
        try:
            return ExternalResourceResponse(
                success_status=True,
                data=ReportResponseDynamodbAdapter(
                    self._table.get_item(Key={"report_name": report_name})
                ),
                error=None,
            )

        except KeyError:
            try:
                self._table.put_item(
                    Item={
                        "report_name": report_name,
                        "last_page_loaded": 1,
                        "last_item_within_the_page_loaded": None,
                    }
                )
                return ExternalResourceResponse(
                    success_status=True,
                    data=ReportResponseDynamodbAdapter(
                        self._table.get_item(Key={"report_name": report_name})
                    ),
                    error=None,
                )
            except Exception as e:
                return ExternalResourceResponse(
                    success_status=False, data=None, error=str(e)
                )
        except Exception as e:
            return ExternalResourceResponse(
                success_status=False, data=None, error=str(e)
            )

    def update_dynamo_db_about_successful_load(
        self, report_name: str, page_loaded: int, last_item_index_loaded: int
    ) -> ExternalResourceResponse:
        try:
            return ExternalResourceResponse(
                success_status=True,
                data=self._table.update_item(
                    Key={"report_name": report_name},
                    UpdateExpression="SET last_page_loaded = :current_page, last_item_within_the_page_loaded = "
                    ":last_item_index_loaded",
                    ExpressionAttributeValues={
                        ":current_page": page_loaded,
                        ":last_item_index_loaded": last_item_index_loaded,
                    },
                ),
                error=None,
            )
        except Exception as e:
            return ExternalResourceResponse(
                success_status=False, data=None, error=str(e)
            )
