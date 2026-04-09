from app.services.erp_formats.sap_fi_formatter import SAPFIFormatter
from app.services.erp_formats.sage_formatter import SageFormatter
from app.services.erp_formats.cegid_formatter import CegidFormatter

FORMATTERS = {
    "sap_fi": SAPFIFormatter,
    "sage": SageFormatter,
    "cegid": CegidFormatter,
}
