# 16 — Problem Validation and Business Case

## 1. Validation status

The workflow is grounded in a plausible recurring AP process, but this package does not claim that customer interviews or a production pilot have been completed. Treat the pain points and segment sizing as hypotheses until validated with real AP/procurement/finance practitioners.

## 2. Target initial segment

Small and mid-sized distributors, manufacturers and service businesses that:
- receive supplier invoices from multiple vendors;
- create and use purchase orders;
- maintain goods receipt/delivery records;
- have separate AP, procurement/warehouse and finance responsibilities;
- currently coordinate invoice discrepancies through email, spreadsheets or chat.

Avoid targeting businesses that have no PO/GRN process; a three-way-match workflow creates little value where these records do not exist.

## 3. Problem hypotheses to validate

| Hypothesis | How to validate | Evidence to record |
|---|---|---|
| AP staff spend time searching for PO/GRN evidence | Interview 3–5 AP staff; ask them to walk through a recent exception | Steps, systems, average minutes and handoff count |
| Quantity/price exceptions require another department | Interview procurement/warehouse and AP together | Who owns the fact, how it is sent and delays |
| Finance receives incomplete approval packets | Ask finance approvers to inspect anonymized historical packet structure | Missing evidence categories and approval rework |
| Duplicate invoice risk is a meaningful blocker | Ask AP lead how duplicate checks work today | Match keys, false positive/negative cases, controls |
| Team chat is already used for cross-functional handoffs | Observe one real workflow (with permission) | Channel, message pattern, whether history is used as evidence |

## 4. Interview questions

1. Walk me through the last invoice that could not be approved immediately.
2. Which records did you need to find to resolve it?
3. Who had the missing information, and how did you reach them?
4. What caused the most delay: extraction, PO matching, goods receipt, policy exception or approval?
5. What is the most common reason an invoice is sent back?
6. How do you detect duplicate invoices today?
7. What would you never allow an automated system to do without a person?
8. Which audit evidence must remain available later?
9. What systems or chat tools are actually used?
10. What would make you trust or reject an agent-prepared approval packet?

Do not collect confidential invoices during a casual interview. Ask for a synthetic or anonymized walkthrough.

## 5. Business value model

Measure rather than claim. For a pilot, capture baseline and post-pilot values:

- `handling_minutes_per_invoice`
- `handoffs_per_exception`
- `time_to_first_owner_response`
- `time_from_invoice_received_to_approval`
- `rework_rate` (case reopened or returned)
- `duplicate_hold_count`

Potential time saved per month (not a result claim):

`monthly_minutes_saved = monthly_invoice_volume × (baseline_minutes - assisted_minutes)`

Potential labor value:

`monthly_labor_value = monthly_minutes_saved / 60 × loaded_hourly_cost`

Report volume, sample size and measurement period. Do not imply that this model includes all software, implementation or control costs.

## 6. Hackathon-safe evidence

For the submission, use synthetic data and present the product as a pilotable workflow hypothesis. The most credible proof is a working end-to-end case, deterministic tests and clear human controls—not an invented customer testimonial or unsupported ROI number.
