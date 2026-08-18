# Machine Learning Foundations

Supervised learning estimates a target function from labeled examples. A useful learning system must generalize beyond the training set, so evaluation uses held-out data, cross-validation, and metrics aligned with the decision cost. High training performance with weak validation performance is evidence of overfitting and can be addressed through better data, regularization, reduced capacity, or revised features.

Bias describes systematic error from restrictive assumptions; variance describes sensitivity to the sampled training data. Model selection balances the two. Learning curves help diagnose whether additional data, additional capacity, or regularization is the most promising intervention.

Retrieval-augmented generation separates knowledge retrieval from language generation. Documents are cleaned, divided into overlapping semantic chunks, embedded, and indexed. At query time, query embeddings retrieve nearby chunks. A generation prompt includes the retrieved evidence and must preserve source identifiers so outputs remain auditable.

Production ML requires monitoring input quality, distribution drift, prediction distributions, latency, and downstream outcomes. Retraining should be triggered by validated degradation rather than elapsed time alone. Every release needs reproducible data lineage, offline evaluation, safe rollout, and rollback criteria.
