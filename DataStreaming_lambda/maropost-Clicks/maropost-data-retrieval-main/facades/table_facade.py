from typing import Dict

from mypy_boto3_dynamodb.service_resource import Table


class TableFacade:
    def __init__(self, service_resource: Table):
        self._service_resource = service_resource

    def get_item(self, Key: Dict):
        return self._service_resource.get_item(Key=Key)

    def put_item(self, Item: Dict):
        return self._service_resource.put_item(Item=Item)

    def update_item(
        self, Key: Dict, UpdateExpression: str, ExpressionAttributeValues: Dict
    ):
        return self._service_resource.update_item(
            Key=Key,
            UpdateExpression=UpdateExpression,
            ExpressionAttributeValues=ExpressionAttributeValues,
        )
