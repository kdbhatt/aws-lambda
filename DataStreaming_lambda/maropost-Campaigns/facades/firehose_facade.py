import json
from abc import ABCMeta, abstractmethod

from mypy_boto3_firehose import FirehoseClient

from model import ExternalResourceResponse


class AbstractFirehoseFacade(object, metaclass=ABCMeta):
    @abstractmethod
    def load_data(self, stream_name: str, data) -> ExternalResourceResponse:
        pass


class FakeFirehoseFacadeBroken(AbstractFirehoseFacade):
    def load_data(self, stream_name: str, data) -> ExternalResourceResponse:
        return ExternalResourceResponse(
            success_status=False, data=None, error="🤖 JEFF BEZOS HAS BLOCKED YOU 🤖"
        )


class FakeFirehoseFacadeWorking(AbstractFirehoseFacade):
    def load_data(self, stream_name: str, data) -> ExternalResourceResponse:
        return ExternalResourceResponse(success_status=True, data={}, error=None)


class FirehoseFacade(AbstractFirehoseFacade):
    def __init__(self, firehose_client: FirehoseClient):
        self._firehose_client = firehose_client

    def load_data(self, stream_name: str, data) -> ExternalResourceResponse:
        try:
            return ExternalResourceResponse(
                success_status=True,
                data=self._firehose_client.put_record_batch(
                    DeliveryStreamName=stream_name,
                    Records=[{"Data": json.dumps(e)} for e in data],
                ),
                error=None,
            )
        except Exception as e:
            return ExternalResourceResponse(
                success_status=False, data=None, error=str(e)
            )
