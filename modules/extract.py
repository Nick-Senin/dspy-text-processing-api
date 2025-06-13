import dspy

class ExtractTransformations(dspy.Signature):
    """Extract transformations with initial states, results and detailed transformations description from text. Initial state transformed into result under the action of transformation. The transformation should not be obvious from the initial state and result."""
    initial_text: str = dspy.InputField(desc="Initial input text")
    transformations: list[dict[str, str]] = dspy.OutputField(desc="Transformations list with initial states, results and transformations")

class TransformationExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        # Use ChainOfThought to allow the optimizer to insert demonstrations.
        self.extractor = dspy.ChainOfThought(ExtractTransformations)

    def forward(self, initial_text):
        return self.extractor(initial_text=initial_text)