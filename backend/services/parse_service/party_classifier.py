import re
from dataclasses import dataclass
from typing import Optional

LEGAL_MARKERS_RU = r"""
    \b(ООО|АО|ПАО|ЗАО|ОАО|НКО|ФГУП|ГУП|МУП|СПАО|САО|НПАО|ПК|
       ТСЖ|ЖСК|АНО|ФОНД|АСОЦИАЦИЯ|СРО|КФХ|ПО|ПТК|Унитарн\w*\s+предпр\w*|
       МЧС|МИНОБОРОНЫ|МИНИСТЕРСТВО|ЦЕНТР|УПРАВЛЕНИЕ|ИНСТИТУТ|
       АВИАКОМПАНИЯ|АЭРОФЛОТ|AIRLINES|MINISTRY|ГУ\s+МЧС|ФГБУ)
    \b
"""

LEGAL_MARKERS_INTL = r"""
    \b(LLC|INC\.?|L\.?T\.?D\.?|LTD\.?|GMBH|AG|S\.?A\.?|BV|N\.?V\.?|OY|AB|
       S\.?R\.?O\.?|S\.?A\.?R\.?L\.?|PLC|LLP|PTE\.?\s+LTD\.?|SAS|S\.?A\.?U\.?)
    \b
"""

IE_MARKERS = r'\b(ИП|Индивидуальн\w+\s+предпринимател\w+)\b'

FIO_THREE = r"^[А-ЯЁ][а-яё'-]+?\s+[А-ЯЁ][а-яё'-]+?\s+[А-ЯЁ][а-яё'-]+$"
FIO_TWO = r"^[А-ЯЁ][а-яё'-]+?\s+[А-ЯЁ][а-яё'-]+$"
FIO_INITS = r"^[А-ЯЁ][а-яё'-]+?\s+[А-ЯЁ]\.[А-ЯЁ]\.$"
FIO_LAT = r"^[A-Z][A-Za-z'-]+(\s+[A-Z][A-Za-z'-]+){1,2}$"

ORG_KEYWORDS = [
    'компания',
    'банк',
    'страховая',
    'университет',
    'институт',
    'завод',
    'фабрика',
    'кооператив',
    'товарищество',
    'партнёрство',
    'company',
    'bank',
    'university',
    'institute',
    'foundation',
    'association',
    'cooperative',
    'partnership',
]

QUOTES = r"[«»\"'„“”]"


@dataclass
class PartyClassification:
    """Результат классификации стороны."""

    category: str
    confidence: float
    normalized: str


class PartyClassifier:
    """Класс для классификации сторон (операторов)."""

    def __init__(self):
        self.legal_markers_ru = re.compile(LEGAL_MARKERS_RU, re.X | re.IGNORECASE)
        self.legal_markers_intl = re.compile(LEGAL_MARKERS_INTL, re.X | re.IGNORECASE)
        self.ie_markers = re.compile(IE_MARKERS, re.X | re.IGNORECASE)

    def _normalize(self, s: Optional[str]) -> str:
        txt = (s or '').strip()
        txt = re.sub(QUOTES, ' ', txt)
        txt = re.sub(r'\s+', ' ', txt)
        return txt.strip()

    def classify(self, s: Optional[str]) -> PartyClassification:
        norm = self._normalize(s)
        upper = norm.upper()

        if self.legal_markers_ru.search(upper) or self.legal_markers_intl.search(upper):
            return PartyClassification('legal_entity', 0.98, norm)

        if self.ie_markers.search(upper):
            return PartyClassification('individual_entrepreneur', 0.95, norm)

        if re.match(FIO_THREE, norm) or re.match(FIO_INITS, norm) or re.match(FIO_TWO, norm):
            return PartyClassification('individual', 0.9, norm)
        if re.match(FIO_LAT, norm):
            return PartyClassification('individual', 0.8, norm)

        if any(w in norm.lower() for w in ORG_KEYWORDS):
            return PartyClassification('likely_legal_entity', 0.6, norm)

        return PartyClassification('unknown', 0.3, norm)
