from app.services.lms.base_connector import BaseLMSConnector
from app.services.lms.cornerstone_connector import CornerstoneConnector
from app.services.lms.learning360_connector import Learning360Connector
from app.services.lms.talentlms_connector import TalentLMSConnector

CONNECTORS: dict[str, type[BaseLMSConnector]] = {
    "cornerstone": CornerstoneConnector,
    "360learning": Learning360Connector,
    "talentlms": TalentLMSConnector,
}


def get_connector(provider: str, config: dict | None = None) -> BaseLMSConnector:
    """Factory to get a connector by provider name."""
    connector_cls = CONNECTORS.get(provider)
    if not connector_cls:
        raise ValueError(f"Unknown LMS provider: {provider}")
    return connector_cls(config=config or {})
