from .proxy import ProxyPool 

class Config:
    def get_rules(self):
        pass
    
    def get_proxy_pool(self) -> ProxyPool:
        pass

    def from_json(self, path: str) -> Config:
        pass
