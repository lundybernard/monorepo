from dataclasses import dataclass

KEY2_DEFAULT = "mono_core.database: KEY2_DEFAULT"


@dataclass
class DatabaseClient:
    """Example client class"""

    key1: str
    key2: str = KEY2_DEFAULT

    # Define a dataclass with the configuration keys your class requires
    @dataclass
    class Config:
        key1: str
        key2: str = KEY2_DEFAULT

    @classmethod
    def from_config(cls, config: Config) -> "DatabaseClient":
        return cls(config.key1, config.key2)

    def fetch_data(self) -> str:
        return f"DatabaseClient data: key1={self.key1}, key2={self.key2}"
