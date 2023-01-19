This script takes in 4 (plaintext) databases (Florida, Ohio, NIS2018, NIS2019), and calculates
1. R-score and V-score for Always Encrypted determinstic encryption, and
2. R-score for Always Encrypted random encryption.
For randomized encryption, V-score does not make sense since some classes can be partially correct.

Extraction of the ciphertext/B+ trees is not shown here, and also not required to calculate the R- and V-scores.
