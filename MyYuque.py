from yuque_py import Yuque

from MyDoc import MyDoc
from MyRepo import MyRepo


class MyYuque(Yuque):
    def __init__(self, api_host: str, user_token: str):
        super(MyYuque, self).__init__(api_host, user_token)
        self.docs = MyDoc(self._client)
        self.repos = MyRepo(self._client)
