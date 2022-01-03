import typing

from yuque_py.models import Doc


class MyDoc(Doc):
    def lists(
            self, namespace: str, data: typing.Optional[typing.Dict] = None
    ) -> typing.Dict:
        assert namespace
        api = f"repos/{namespace}/docs"
        return self._client.request(api, method="GET", requests_data=data)