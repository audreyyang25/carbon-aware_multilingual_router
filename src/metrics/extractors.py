import re


class BaseAnswerExtractor:
    """Base class for extracting answers from model responses."""

    def extract(self, response, extraction_params=None):
        """Extract answer from model response."""
        raise NotImplementedError("Subclasses must implement extract()")


# GreenServ leftover, unused here: every benchmark uses the multiple_choice or numeric extractor
# (config/datasets.yaml). get_extractor still falls back to it for "regex_<pattern>" methods.
class RegexAnswerExtractor(BaseAnswerExtractor):
    """Extract answers using regular expressions."""

    def __init__(self, pattern="(?<=: )(.+)"):
        self.pattern = pattern

    def extract(self, response, extraction_params=None):
        """Extract answer from response using regex pattern."""
        if not response:
            return ""

        try:
            match = re.search(self.pattern, response)
            return (
                match.group(1).strip() if match and match.groups() else response.strip()
            )
        except Exception as e:
            print(f"Regex extraction error: {e}")
            return response.strip()


# A number with optional thousands groups (1,000 / 1.000 / 1 000) and decimals.
# \d also matches native digits (e.g. Thai), which float() understands.
NUMBER_PATTERN = r"\d+(?:[,.\u00a0\u202f ]\d{3})*(?:[.,]\d+)?"


def canonical_number(text):
    """Parse a number string in US or European format; return e.g. "1000" or "2.5" (or "")."""
    if text is None:
        return ""
    s = re.sub(r"[\u00a0\u202f ]", "", str(text).strip()).rstrip(".,")
    if not s:
        return ""
    if "," in s and "." in s:
        # Whichever separator comes last is the decimal point
        decimal = "," if s.rfind(",") > s.rfind(".") else "."
        s = s.replace("." if decimal == "," else ",", "").replace(decimal, ".")
    elif "," in s or "." in s:
        sep = "," if "," in s else "."
        if re.fullmatch(r"\d{1,3}(?:" + re.escape(sep) + r"\d{3})+", s):
            s = s.replace(sep, "")  # thousands separators
        else:
            s = s.replace(",", ".")
    try:
        value = float(s)
    except ValueError:
        return ""
    return str(int(value)) if value.is_integer() else str(value)


class NumericAnswerExtractor(BaseAnswerExtractor):
    """Extract numeric answers, first from 'Answer: X' format, then last number in text.

    Set extraction_params={"allow_fallback": False} for truncated outputs: without an
    "Answer:" line the last number is just an intermediate step, so nothing is extracted.
    """

    def extract(self, response, extraction_params=None):
        """Extract numeric answer from response."""
        if not response:
            return ""
        allow_fallback = (extraction_params or {}).get("allow_fallback", True)

        try:
            answer_match = re.search(
                r"Answer:\s*[*$]*\s*(" + NUMBER_PATTERN + ")", response
            )
            if answer_match:
                return canonical_number(answer_match.group(1))
            if not allow_fallback:
                return ""
            numbers = re.findall(NUMBER_PATTERN, response)
            return canonical_number(numbers[-1]) if numbers else ""
        except Exception:
            return ""


class MultipleChoiceExtractor(BaseAnswerExtractor):
    """Extract multiple choice answers (A, B, C, D)."""

    def extract(self, response, extraction_params=None):
        """Extract multiple choice answer from response (a standalone letter, so the
        "A" in "Answer" doesn't count)."""
        pattern = (extraction_params or {}).get("pattern", r"\b([A-D])\b")
        match = re.search(pattern, response or "")
        return match.group(1) if match else ""


# GreenServ leftover, unused here: every benchmark uses the multiple_choice or numeric extractor;
# this is only get_extractor's fallback for an unknown method.
class RawTextExtractor(BaseAnswerExtractor):
    """Use the full text as the answer (e.g., for summarization)."""

    def extract(self, response, extraction_params=None):
        """Return the raw response text."""
        return response.strip() if response else ""


EXTRACTORS = {
    "raw": RawTextExtractor(),
    "multiple_choice": MultipleChoiceExtractor(),
    "regex": RegexAnswerExtractor(),
    "numeric": NumericAnswerExtractor(),
}


def get_extractor(extraction_method="raw"):
    """Get the appropriate extractor based on method name."""

    if extraction_method == "numeric":
        return NumericAnswerExtractor()
    if extraction_method.startswith("regex_") and "(?!.*\\d)" in extraction_method:
        return NumericAnswerExtractor()
    if extraction_method.startswith("regex_"):
        pattern = extraction_method[6:]
        return RegexAnswerExtractor(pattern)

    return EXTRACTORS.get(extraction_method, RawTextExtractor())
