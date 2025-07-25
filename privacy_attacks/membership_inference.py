import random

def membership_inference(model_predict, samples, true_training_data):
    """
    model_predict: function taking a sample and returning a confidence score or logits
    samples: list of test samples (some in training, some not)
    true_training_data: set/list of samples actually used to train
    """
    leaked = []
    for s in samples:
        conf = model_predict(s)
        # Naive threshold: if confidence > 0.95, guess it was in training set
        if conf > 0.95 and s in true_training_data:
            leaked.append(s)
    print(f"Membership inference leak detected for: {leaked}")
    return leaked

# Usage: 
# membership_inference(your_model.predict, your_samples, your_train_data)
