# -*- coding: utf-8 -*-
import re
from types import UnicodeType
import unicodedata


def slugify(value):
    """
    Normalizes string, removes non-alpha characters, and converts hyphens 
    and spaces to underscores.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return re.sub('[-\s]+', '_', value)

# default unicode character mapping ( you may not see some chars, leave as is )
char_map = {u'À': 'A', u'Á': 'A', u'Â': 'A', u'Ã': 'A', u'Ä': 'Ae', u'Å': 'A', u'Æ': 'A', u'Ā': 'A', u'Ą': 'A', u'Ă': 'A', u'Ç': 'C', u'Ć': 'C', u'Č': 'C', u'Ĉ': 'C', u'Ċ': 'C', u'Ď': 'D', u'Đ': 'D', u'È': 'E', u'É': 'E', u'Ê': 'E', u'Ë': 'E', u'Ē': 'E', u'Ę': 'E', u'Ě': 'E', u'Ĕ': 'E', u'Ė': 'E', u'Ĝ': 'G', u'Ğ': 'G', u'Ġ': 'G', u'Ģ': 'G', u'Ĥ': 'H', u'Ħ': 'H', u'Ì': 'I', u'Í': 'I', u'Î': 'I', u'Ï': 'I', u'Ī': 'I', u'Ĩ': 'I', u'Ĭ': 'I', u'Į': 'I', u'İ': 'I', u'Ĳ': 'IJ', u'Ĵ': 'J', u'Ķ': 'K', u'Ľ': 'K', u'Ĺ': 'K', u'Ļ': 'K', u'Ŀ': 'K', u'Ł': 'L', u'Ñ': 'N', u'Ń': 'N', u'Ň': 'N', u'Ņ': 'N', u'Ŋ': 'N', u'Ò': 'O', u'Ó': 'O', u'Ô': 'O', u'Õ': 'O', u'Ö': 'Oe', u'Ø': 'O', u'Ō': 'O', u'Ő': 'O', u'Ŏ': 'O', u'Œ': 'OE', u'Ŕ': 'R', u'Ř': 'R', u'Ŗ': 'R', u'Ś': 'S', u'Ş': 'S', u'Ŝ': 'S', u'Ș': 'S', u'Š': 'S', u'Ť': 'T', u'Ţ': 'T', u'Ŧ': 'T', u'Ț': 'T', u'Ù': 'U', u'Ú': 'U', u'Û': 'U', u'Ü': 'Ue', u'Ū': 'U', u'Ů': 'U', u'Ű': 'U', u'Ŭ': 'U', u'Ũ': 'U', u'Ų': 'U', u'Ŵ': 'W', u'Ŷ': 'Y', u'Ÿ': 'Y', u'Ý': 'Y', u'Ź': 'Z', u'Ż': 'Z', u'Ž': 'Z', u'à': 'a', u'á': 'a', u'â': 'a', u'ã': 'a', u'ä': 'ae', u'ā': 'a', u'ą': 'a', u'ă': 'a', u'å': 'a', u'æ': 'ae', u'ç': 'c', u'ć': 'c', u'č': 'c', u'ĉ': 'c', u'ċ': 'c', u'ď': 'd', u'đ': 'd', u'è': 'e', u'é': 'e', u'ê': 'e', u'ë': 'e', u'ē': 'e', u'ę': 'e', u'ě': 'e', u'ĕ': 'e', u'ė': 'e', u'ƒ': 'f', u'ĝ': 'g', u'ğ': 'g', u'ġ': 'g', u'ģ': 'g', u'ĥ': 'h', u'ħ': 'h', u'ì': 'i', u'í': 'i', u'î': 'i', u'ï': 'i', u'ī': 'i', u'ĩ': 'i', u'ĭ': 'i', u'į': 'i', u'ı': 'i', u'ĳ': 'ij', u'ĵ': 'j', u'ķ': 'k', u'ĸ': 'k', u'ł': 'l', u'ľ': 'l', u'ĺ': 'l', u'ļ': 'l', u'ŀ': 'l', u'ñ': 'n', u'ń': 'n', u'ň': 'n', u'ņ': 'n', u'ŉ': 'n', u'ŋ': 'n', u'ò': 'o', u'ó': 'o', u'ô': 'o', u'õ': 'o', u'ö': 'oe', u'ø': 'o', u'ō': 'o', u'ő': 'o', u'ŏ': 'o', u'œ': 'oe', u'ŕ': 'r', u'ř': 'r', u'ŗ': 'r', u'ś': 's', u'š': 's', u'ť': 't', u'ù': 'u', u'ú': 'u', u'û': 'u', u'ü': 'ue', u'ū': 'u', u'ů': 'u', u'ű': 'u', u'ŭ': 'u', u'ũ': 'u', u'ų': 'u', u'ŵ': 'w', u'ÿ': 'y', u'ý': 'y', u'ŷ': 'y', u'ż': 'z', u'ź': 'z', u'ž': 'z', u'ß': 'ss', u'ſ': 'ss', u'Α': 'A', u'Ά': 'A', u'Ἀ': 'A', u'Ἁ': 'A', u'Ἂ': 'A', u'Ἃ': 'A', u'Ἄ': 'A', u'Ἅ': 'A', u'Ἆ': 'A', u'Ἇ': 'A', u'ᾈ': 'A', u'ᾉ': 'A', u'ᾊ': 'A', u'ᾋ': 'A', u'ᾌ': 'A', u'ᾍ': 'A', u'ᾎ': 'A', u'ᾏ': 'A', u'Ᾰ': 'A', u'Ᾱ': 'A', u'Ὰ': 'A', u'Ά': 'A', u'ᾼ': 'A', u'Β': 'B', u'Γ': 'G', u'Δ': 'D', u'Ε': 'E', u'Έ': 'E', u'Ἐ': 'E', u'Ἑ': 'E', u'Ἒ': 'E', u'Ἓ': 'E', u'Ἔ': 'E', u'Ἕ': 'E', u'Έ': 'E', u'Ὲ': 'E', u'Ζ': 'Z', u'Η': 'I', u'Ή': 'I', u'Ἠ': 'I', u'Ἡ': 'I', u'Ἢ': 'I', u'Ἣ': 'I', u'Ἤ': 'I', u'Ἥ': 'I', u'Ἦ': 'I', u'Ἧ': 'I', u'ᾘ': 'I', u'ᾙ': 'I', u'ᾚ': 'I', u'ᾛ': 'I', u'ᾜ': 'I', u'ᾝ': 'I', u'ᾞ': 'I', u'ᾟ': 'I', u'Ὴ': 'I', u'Ή': 'I', u'ῌ': 'I', u'Θ': 'TH', u'Ι': 'I', u'Ί': 'I', u'Ϊ': 'I', u'Ἰ': 'I', u'Ἱ': 'I', u'Ἲ': 'I', u'Ἳ': 'I', u'Ἴ': 'I', u'Ἵ': 'I', u'Ἶ': 'I', u'Ἷ': 'I', u'Ῐ': 'I', u'Ῑ': 'I', u'Ὶ': 'I', u'Ί': 'I', u'Κ': 'K', u'Λ': 'L', u'Μ': 'M', u'Ν': 'N', u'Ξ': 'KS', u'Ο': 'O', u'Ό': 'O', u'Ὀ': 'O', u'Ὁ': 'O', u'Ὂ': 'O', u'Ὃ': 'O', u'Ὄ': 'O', u'Ὅ': 'O', u'Ὸ': 'O', u'Ό': 'O', u'Π': 'P', u'Ρ': 'R', u'Ῥ': 'R', u'Σ': 'S', u'Τ': 'T', u'Υ': 'Y', u'Ύ': 'Y', u'Ϋ': 'Y', u'Ὑ': 'Y', u'Ὓ': 'Y', u'Ὕ': 'Y', u'Ὗ': 'Y', u'Ῠ': 'Y', u'Ῡ': 'Y', u'Ὺ': 'Y', u'Ύ': 'Y', u'Φ': 'F', u'Χ': 'X', u'Ψ': 'PS', u'Ω': 'O', u'Ώ': 'O', u'Ὠ': 'O', u'Ὡ': 'O', u'Ὢ': 'O', u'Ὣ': 'O', u'Ὤ': 'O', u'Ὥ': 'O', u'Ὦ': 'O', u'Ὧ': 'O', u'ᾨ': 'O', u'ᾩ': 'O', u'ᾪ': 'O', u'ᾫ': 'O', u'ᾬ': 'O', u'ᾭ': 'O', u'ᾮ': 'O', u'ᾯ': 'O', u'Ὼ': 'O', u'Ώ': 'O', u'ῼ': 'O', u'α': 'a', u'ά': 'a', u'ἀ': 'a', u'ἁ': 'a', u'ἂ': 'a', u'ἃ': 'a', u'ἄ': 'a', u'ἅ': 'a', u'ἆ': 'a', u'ἇ': 'a', u'ᾀ': 'a', u'ᾁ': 'a', u'ᾂ': 'a', u'ᾃ': 'a', u'ᾄ': 'a', u'ᾅ': 'a', u'ᾆ': 'a', u'ᾇ': 'a', u'ὰ': 'a', u'ά': 'a', u'ᾰ': 'a', u'ᾱ': 'a', u'ᾲ': 'a', u'ᾳ': 'a', u'ᾴ': 'a', u'ᾶ': 'a', u'ᾷ': 'a', u'β': 'b', u'γ': 'g', u'δ': 'd', u'ε': 'e', u'έ': 'e', u'ἐ': 'e', u'ἑ': 'e', u'ἒ': 'e', u'ἓ': 'e', u'ἔ': 'e', u'ἕ': 'e', u'ὲ': 'e', u'έ': 'e', u'ζ': 'z', u'η': 'i', u'ή': 'i', u'ἠ': 'i', u'ἡ': 'i', u'ἢ': 'i', u'ἣ': 'i', u'ἤ': 'i', u'ἥ': 'i', u'ἦ': 'i', u'ἧ': 'i', u'ᾐ': 'i', u'ᾑ': 'i', u'ᾒ': 'i', u'ᾓ': 'i', u'ᾔ': 'i', u'ᾕ': 'i', u'ᾖ': 'i', u'ᾗ': 'i', u'ὴ': 'i', u'ή': 'i', u'ῂ': 'i', u'ῃ': 'i', u'ῄ': 'i', u'ῆ': 'i', u'ῇ': 'i', u'θ': 'th', u'ι': 'i', u'ί': 'i', u'ϊ': 'i', u'ΐ': 'i', u'ἰ': 'i', u'ἱ': 'i', u'ἲ': 'i', u'ἳ': 'i', u'ἴ': 'i', u'ἵ': 'i', u'ἶ': 'i', u'ἷ': 'i', u'ὶ': 'i', u'ί': 'i', u'ῐ': 'i', u'ῑ': 'i', u'ῒ': 'i', u'ΐ': 'i', u'ῖ': 'i', u'ῗ': 'i', u'κ': 'k', u'λ': 'l', u'μ': 'm', u'ν': 'n', u'ξ': 'ks', u'ο': 'o', u'ό': 'o', u'ὀ': 'o', u'ὁ': 'o', u'ὂ': 'o', u'ὃ': 'o', u'ὄ': 'o', u'ὅ': 'o', u'ὸ': 'o', u'ό': 'o', u'π': 'p', u'ρ': 'r', u'ῤ': 'r', u'ῥ': 'r', u'σ': 's', u'ς': 's', u'τ': 't', u'υ': 'y', u'ύ': 'y', u'ϋ': 'y', u'ΰ': 'y', u'ὐ': 'y', u'ὑ': 'y', u'ὒ': 'y', u'ὓ': 'y', u'ὔ': 'y', u'ὕ': 'y', u'ὖ': 'y', u'ὗ': 'y', u'ὺ': 'y', u'ύ': 'y', u'ῠ': 'y', u'ῡ': 'y', u'ῢ': 'y', u'ΰ': 'y', u'ῦ': 'y', u'ῧ': 'y', u'φ': 'f', u'χ': 'x', u'ψ': 'ps', u'ω': 'o', u'ώ': 'o', u'ὠ': 'o', u'ὡ': 'o', u'ὢ': 'o', u'ὣ': 'o', u'ὤ': 'o', u'ὥ': 'o', u'ὦ': 'o', u'ὧ': 'o', u'ᾠ': 'o', u'ᾡ': 'o', u'ᾢ': 'o', u'ᾣ': 'o', u'ᾤ': 'o', u'ᾥ': 'o', u'ᾦ': 'o', u'ᾧ': 'o', u'ὼ': 'o', u'ώ': 'o', u'ῲ': 'o', u'ῳ': 'o', u'ῴ': 'o', u'ῶ': 'o', u'ῷ': 'o', u'¨': '', u'΅': '', u'᾿': '', u'῾': '', u'῍': '', u'῝': '', u'῎': '', u'῞': '', u'῏': '', u'῟': '', u'῀': '', u'῁': '', u'΄': '', u'΅': '', u'`': '', u'῭': '', u'ͺ': '', u'᾽': '', u'А': 'A', u'Б': 'B', u'В': 'V', u'Г': 'G', u'Д': 'D', u'Е': 'E', u'Ё': 'E', u'Ж': 'ZH', u'З': 'Z', u'И': 'I', u'Й': 'I', u'К': 'K', u'Л': 'L', u'М': 'M', u'Н': 'N', u'О': 'O', u'П': 'P', u'Р': 'R', u'С': 'S', u'Т': 'T', u'У': 'U', u'Ф': 'F', u'Х': 'KH', u'Ц': 'TS', u'Ч': 'CH', u'Ш': 'SH', u'Щ': 'SHCH', u'Ы': 'Y', u'Э': 'E', u'Ю': 'YU', u'Я': 'YA', u'а': 'A', u'б': 'B', u'в': 'V', u'г': 'G', u'д': 'D', u'е': 'E', u'ё': 'E', u'ж': 'ZH', u'з': 'Z', u'и': 'I', u'й': 'I', u'к': 'K', u'л': 'L', u'м': 'M', u'н': 'N', u'о': 'O', u'п': 'P', u'р': 'R', u'с': 'S', u'т': 'T', u'у': 'U', u'ф': 'F', u'х': 'KH', u'ц': 'TS', u'ч': 'CH', u'ш': 'SH', u'щ': 'SHCH', u'ы': 'Y', u'э': 'E', u'ю': 'YU', u'я': 'YA', u'Ъ': '', u'ъ': '', u'Ь': '', u'ь': '', u'ð': 'd', u'Ð': 'D', u'þ': 'th', u'Þ': 'TH',
            u'ა': 'a', u'ბ': 'b', u'გ': 'g', u'დ': 'd', u'ე': 'e', u'ვ': 'v', u'ზ': 'z', u'თ': 't', u'ი': 'i', u'კ': 'k', u'ლ': 'l', u'მ': 'm', u'ნ': 'n', u'ო': 'o', u'პ': 'p', u'ჟ': 'zh', u'რ': 'r', u'ს': 's', u'ტ': 't', u'უ': 'u', u'ფ': 'p', u'ქ': 'k', u'ღ': 'gh', u'ყ': 'q', u'შ': 'sh', u'ჩ': 'ch', u'ც': 'ts', u'ძ': 'dz', u'წ': 'ts', u'ჭ': 'ch', u'ხ': 'kh', u'ჯ': 'j', u'ჰ': 'h'}


def replace_char(m):
    char = m.group()
    if char in char_map:
        return char_map[char]
    else:
        return char


def slughifi(value, overwrite_char_map={}):
    """
        High Fidelity slugify - slughifi.py, v 0.1

        Examples :

        >>> text = 'C\'est déjà l\'été.'

        >>> slughifi(text)
        'cest-deja-lete'

        >>> slughifi(text, overwrite_char_map={u'\': '-',})
        'c-est-deja-l-ete'

        >>> slughifi(text, do_slugify=False)
        "C'est deja l'ete."

        # Normal slugify removes accented characters
        >>> slugify(text)
        'cest-dj-lt'

    """

    # unicodification
    if type(value) != UnicodeType:
        value = unicode(value, 'utf-8', 'ignore')

    # overwrite chararcter mapping
    char_map.update(overwrite_char_map)

    # try to replace chars
    value = re.sub('[^a-zA-Z0-9\\s\\-]{1}', replace_char, value)

    value = slugify(value)

    return value.encode('ascii', 'ignore')
