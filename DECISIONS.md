# Engineering Decisions

## 1. Logistic regression for credit-risk probability
A two-feature logistic-regression model is used because the official problem only requires small-business credit-risk scoring from monthly cash flow and registration age. It is fast to train, easy to inspect, and produces a probability that maps cleanly to the three required decisions.

## 2. Directional behaviour is protected by model training and a real-model test
The generated training data makes higher cash flow reduce default risk. Training fails if the learned cash-flow coefficient has the wrong sign, and a behavioural test verifies across several registration ages that increasing cash flow never raises predicted default probability.

## 3. Decision thresholds live in the domain layer
The model predicts probability only. The domain policy maps probability below 0.25 to `auto_approve`, from 0.25 to below 0.55 to `manual_review`, and 0.55 or above to `reject`. This keeps the business decision independent of the model adapter.

## 4. Redis is the compose supporting service and operational extension
The core prediction can run with an in-memory store, while Docker Compose switches to Redis. Redis stores only a prediction counter, not request fields or personal data. `/v1/stats` exposes that count as the required tested extension, and `/ready` reports unavailable when the configured Redis dependency is not healthy.

## 5. The golden reference file is reviewed data, not generated at test time
`tests/behavioural/golden_cases.json` is committed with fixed expected values from the checked-in model artifact. There is deliberately no automatic golden-file regeneration step. Any future change to those values requires a model change, review, and an explicit commit explaining why the reference changed.
