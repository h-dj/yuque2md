import typing

from yuque_py.models import Repo


class MyRepo(Repo):

    def toc(self, namespace: str) -> typing.Dict:
        assert namespace
        return self._client.request(
            f"repos/{namespace}/toc", method="GET"
        )
