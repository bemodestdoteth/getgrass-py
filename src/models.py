from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Device:
    userAgent: str
    ipAddress: str
    ipScore: int
    countryCode: str
    totalUptime: str
    isConnected: bool
    totalPoints: int
    userId: str
    deviceId: str

@dataclass_json
@dataclass
class User:
    email: str
    userId: str
    username: str