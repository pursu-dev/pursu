# pylint: skip-file
import re

class DatePatterns:
    FORMAL_DATE = r'((31(?!\ (Feb(ruary)?|Apr(il)?|June?|(Sep(?=\b|t)t?|Nov)(ember)?)))|((30|29)(?!\ Feb(ruary)?))|(29(?=\ Feb(ruary)?\ (((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))))|(0?[1-9])|1\d|2[0-8])\ (Jan(uary)?|Feb(ruary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sep(?=\b|t)t?|Nov|Dec)(ember)?)\ ((1[6-9]|[2-9]\d)\d{2})'
    STANDARD_DATE = r'(Jan(uary)?|Feb(ruary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sep(?=\b|t)t?|Nov|Dec)(ember)?)\ (1\d|2\d|0?[1-9])((st|nd|rd|th)?)'
    MM_DD_YYYY = r'((0?[1-9])|1[012])[-\/.](0[1-9]|[12][0-9]|3[01])([- \/.](19|20)\d\d)?'
    #MMDDYYYY = r'(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])((19|20)\d\d)?'
    TIME = r'(\d+) (hour(s?)|week(s?)|day(s?))'
    NATURAL_DEADLINE = r'\b\w+\b (hour(s?)|day(s?)|week(s?))( ?)(from (today|tonight))'

class NamePatterns:
    FIRST_LAST = r'\b[a-zA-Zé]+?\b \b[a-zA-Z]+?\b'
    LAST_COMMA_FIRST = r'\b[a-zA-Z]+?\b, \b[a-zA-Z]+?\b'

class EmailPatterns:
    EMAIL = r'[\+a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+'