import random
import string
from time import sleep

METADATA = {
    "name": "Model Extraction Attack",
    "risk": "Critical",
    "type": "model_extraction",
    "description": "Performs black-box model extraction via adaptive API querying and output mining."
}

class ModelExtractionAttack:
    def __init__(self):
        self.queries = []
        self.extracted_knowledge = {}

    def synth_query(self, label=None):
        """Generate a maximally-informative synthetic query."""
        base = [
            "Explain the difference between supervised and unsupervised learning.",
            "What are the main advantages of transformer-based neural networks?",
            "Write a function in Python to compute the softmax of a list.",
            "Summarize the causes of World War II in three bullet points.",
            "How would you mitigate overfitting in a deep learning model?"
        ]
        if label and label in self.extracted_knowledge:
            # Use previous answers to seed more targeted queries
            return f"Based on your earlier answer: {self.extracted_knowledge[label][:50]}..., can you expand on that?"
        return random.choice(base)

    def run(self, scenario, endpoint, api_key, mode, *args, **kwargs):
        attack_log = []
        knowledge = []
        for i in range(30):  # 30 distinct adaptive queries
            q = self.synth_query(label=None if not knowledge else i-1)
            attack_log.append(q)
            # Simulate: real code would call LLM API with q
            # response = call_api(q, endpoint, api_key)
            response = f"Simulated answer to: {q[:40]}... (answer {i+1})"
            self.extracted_knowledge[f"q{i+1}"] = response
            knowledge.append(response)
            sleep(0.05)
        return {
            "extracted_samples": knowledge[:5],
            "total_queries": len(attack_log),
            "success": True if knowledge else False,
            "details": f"Extracted {len(knowledge)} candidate model secrets/responses"
        }

def run(*args, **kwargs):
    return ModelExtractionAttack().run(*args, **kwargs)
