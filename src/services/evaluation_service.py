from src.metrics.accuracy import QualityMetrics
from src.metrics.extractors import canonical_number, get_extractor
from src.metrics.text_utils import TextNormalizer


class EvaluationService:
    """Scores a model response against the reference answer."""

    def __init__(self):
        self.quality_metrics = QualityMetrics()
        self.text_normalizer = TextNormalizer()

    def evaluate(
        self,
        response,
        reference,
        task_type="default",
        extraction_method="raw",
        evaluation_metric="exact_match",
        truncated=False,
    ):
        """Evaluate response against reference for a specific task type.

        truncated: the output hit max_new_tokens, so only an explicit answer counts.
        """

        extractor = get_extractor(extraction_method)
        extracted_response = extractor.extract(
            response, {"allow_fallback": not truncated}
        )
        skip_normalization = extraction_method == "numeric" or (
            extraction_method.startswith("regex_") and "(?!.*\\d)" in extraction_method
        )

        if skip_normalization:
            normalized_response = extracted_response
            normalized_reference = canonical_number(reference) or str(reference)
        else:
            normalized_response = self.text_normalizer.normalize(extracted_response)
            normalized_reference = self.text_normalizer.normalize(reference)
        score = self.quality_metrics.calculate(
            normalized_response, normalized_reference, metric_type=evaluation_metric
        )

        return score
