# Controlled verifier preflight

Requests attempted: 3; responses received: 3.
Schema compliance: 3/3. Prediction correctness: 3/3.
Input tokens: 1577; output tokens: 117.
Accounted cost: $0.00081800 (provider_reported).

| Example | Expected | Predicted | Schema status | Correct |
|---|---|---|---|---|
| A | SUPPORTED | SUPPORTED | VALID_PREDICTION | True |
| B | UNSUPPORTED | UNSUPPORTED | VALID_PREDICTION | True |
| C | CONTRADICTED | CONTRADICTED | VALID_PREDICTION | True |

## Example A

The evidence explicitly states that the fictional hearing occurred on Monday, directly supporting the claim.

## Example B

The evidence only states that the fictional hearing occurred on Monday and does not provide any information about whether the hearing was recorded.

## Example C

The evidence explicitly states that the fictional hearing occurred on Monday, directly contradicting the claim that it occurred on Tuesday.

No benchmark requests, retries, fallback, prompt tuning, or benchmark-label changes.
Actual usage is recorded; costs are provider-reported when available, otherwise calculated from usage at the verified rates.
Original 35-request plan has 32 requests remaining, none authorized.
Existing source, benchmark, experiment and runtime artifacts were verified unchanged.
