# Adversarial API & Endpoint Stress Test Report (Challenger 1)

**Challenger**: Challenger 1 (Adversarial API & Endpoint Stress Tester)  
**Roles**: critic, specialist  
**Target Milestone**: M1 (Core System Verification, API Route Aliases & Deliverables)  
**Deliverable Path**: `e:\Bangla Scantling\.agents\teamwork\teamwork_challenger_m1_1\handoff.md`  
**Date**: 2026-10-30T06:28:30Z  
**Verdict**: **REJECT**  

---

## Challenge Summary

**Overall risk assessment**: **HIGH**

While the canonical route aliases, ReportLab PDF generation engines, CORS preflight headers, and clean default state calculations function correctly under nominal conditions, rigorous adversarial stress-testing revealed critical failure modes resulting in unhandled `500 Internal Server Error` crashes:
1. **Critical Persistent State Poisoning / Denial of Service**: `POST /api/save-state` permits non-dictionary payloads (e.g., `[]`, `"string"`), which permanently corrupts `saved_state.json` and causes `GET /api/initial-state` to crash with an unhandled 500 for all users on all subsequent requests.
2. **Unhandled 500 on User Form Clearing / Empty Strings**: `LightshipService.calculate_lightship` attempts a direct `float()` conversion on plate thicknesses (`inputs[bound_k]`). When an end-user clears an input field in the web browser (transmitting an empty string `""` or non-numeric string), `POST /api/calculate` and all live PDF endpoints crash with `ValueError: could not convert string to float: ''`.
3. **Unhandled 500 on Type Poisoning in Calculation Engine**: `POST /api/calculate` accepts raw JSON without type checking, directly attempting `.get()` on list bodies and crashing with `AttributeError`.

---

## Challenges

### [Critical] Challenge 1: Permanent DOS via `/api/save-state` State Poisoning
- **Assumption challenged**: The persistence layer assumes any JSON received by `POST /api/save-state` is a well-formed dictionary state representation conforming to the application schema.
- **Attack scenario**: An adversary or errant client sends `POST /api/save-state` with payload `[1, 2, 3]` or `"corrupt"`.
- **Blast radius**: `StateRepository.save_state()` writes the raw JSON list to `saved_state.json`. Subsequently, `StateService.get_initial_state()` executes `for k, v in saved.items():`. Because `saved` is a list, Python throws `AttributeError: 'list' object has no attribute 'items'`, returning an unhandled HTTP 500 on `GET /api/initial-state`. The entire web application fails to boot or load for all clients until the physical file `app/saved_state.json` is manually deleted or restored on the host.
- **Mitigation**:
  1. In `app/api/v1/endpoints_state.py`, validate `if not isinstance(body, dict): return JSONResponse(status_code=400, content={"status": "error", "message": "Payload must be a dictionary"})`.
  2. In `app/services/state_service.py` (`get_initial_state()`), guard: `if saved and isinstance(saved, dict):`.

---

### [High] Challenge 2: Unhandled 500 Crash on Empty String or Non-Numeric Plate Inputs
- **Assumption challenged**: `LightshipService` assumes that any value in `dashboard_inputs` for which `.get(bound_k) is not None` evaluates to `True` is already a valid floating point representation.
- **Attack scenario**: A user clears an input field (e.g. `t_side`, `t_keel`, `t_bottom`) in the Dashboard or Detail Calc form, or enters an annotated string like `"12.0mm"`. The frontend submits `{ "dashboard_inputs": { "t_side": "" } }`.
- **Blast radius**: In `app/services/lightship_service.py` line 142:
  ```python
  elif inputs.get(bound_k) is not None:
      t_val = float(inputs[bound_k])
  ```
  `inputs.get('t_side')` returns `""` (not `None`). The direct call `float("")` or `float("12.0mm")` raises `ValueError: could not convert string to float: ''`. This uncaught exception bubbles up through `CalculationService.compute_all_calculations()`, crashing `POST /api/calculate`, `POST /api/v1/pdf/detail-calc`, `POST /api/v1/pdf/lightship`, and `POST /api/v1/pdf/application-form` with HTTP 500.
- **Mitigation**: Use a safe conversion helper with fallback default in `LightshipService`:
  ```python
  def _to_float(val, default=0.0):
      try:
          if val is None or val == "":
              return default
          return float(val)
      except (ValueError, TypeError):
          return default
  ```
  Replace `t_val = float(inputs[bound_k])` with `t_val = _to_float(inputs.get(bound_k), tmpl["t_def"])`.

---

### [High] Challenge 3: Unhandled 500 Crash on Non-Dict Payload in `/api/calculate`
- **Assumption challenged**: `POST /api/calculate` assumes the JSON request body is always a dictionary.
- **Attack scenario**: A client sends `POST /api/calculate` with payload `[]` or `"string"`.
- **Blast radius**: In `app/api/v1/endpoints_calculation.py`:
  ```python
  body = await request.json()
  updated_state = calc_service.compute_all_calculations(body)
  ```
  Inside `compute_all_calculations(state)`:
  ```python
  inputs = state.get('dashboard_inputs', {}) or {}
  ```
  When `state` is a list, Python raises `AttributeError: 'list' object has no attribute 'get'`, returning HTTP 500 instead of a clean 400/422 validation response. Note that `endpoints_pdf.py` already includes an `isinstance(custom_state, dict)` guard; this defensive check was omitted from `endpoints_calculation.py`.
- **Mitigation**: Add input validation in `app/api/v1/endpoints_calculation.py`:
  ```python
  if not isinstance(body, dict):
      return JSONResponse(status_code=422, content={"detail": "Expected JSON object"})
  ```

---

### [Medium] Challenge 4: Lightship Saved Dimensions & Quantities Corrupted Parsing
- **Assumption challenged**: In `LightshipService.calculate_lightship()`, lines 169-171 and 243-244 use `.get('qty', default_qty)` to provide defaults.
- **Attack scenario**: If a saved plate or angle object exists in state with an empty string (e.g. `{'sn': 1, 'qty': ''}` or `{'sn': 1, 'l': ''}`), `.get('qty', default_qty)` returns `""` because the key exists.
- **Blast radius**: The subsequent `int(saved.get('qty', default_qty))` or `float(saved.get('l', default_l))` raises `ValueError: invalid literal for int() with base 10: ''`, taking down the calculation pipeline with HTTP 500.
- **Mitigation**: Implement safe integer and float sanitizers:
  ```python
  def _to_int(val, default=0):
      try:
          return int(val)
      except (ValueError, TypeError):
          return default
  ```

---

## 1. Observation

### 1.1 Empirical Test Suite Execution
An automated adversarial test harness `tests/adversarial_endpoint_stress.py` was executed against `http://127.0.0.1:8055`.
**Command**:
```powershell
python tests/adversarial_endpoint_stress.py -v
```
**Output Log**:
```
test_01_pdf_route_aliases_get (__main__.TestAdversarialEndpoints.test_01_pdf_route_aliases_get)
Verify all required PDF GET endpoints return valid, uncorrupted PDFs. ... ok
test_02_pdf_route_aliases_post (__main__.TestAdversarialEndpoints.test_02_pdf_route_aliases_post)
Verify all required PDF POST snapshot endpoints return valid, uncorrupted PDFs. ... ok
test_03_cors_preflight_options (__main__.TestAdversarialEndpoints.test_03_cors_preflight_options)
Challenge CORS preflight OPTIONS handling across origins and custom headers. ... ok
test_04_post_empty_json_body (__main__.TestAdversarialEndpoints.test_04_post_empty_json_body)
Adversarially challenge POST endpoints with empty JSON `{}` to ensure no unhandled 500. ... ok
test_05_partial_state_fuzzing (__main__.TestAdversarialEndpoints.test_05_partial_state_fuzzing)
Verify server gracefully handles payloads with missing sections without crashing. ... ok
test_06_null_fields_and_type_boundaries (__main__.TestAdversarialEndpoints.test_06_null_fields_and_type_boundaries)
Adversarially inject null and empty strings into numerical fields. ... 
  (url='http://127.0.0.1:8055/api/v1/pdf/detail-calc') ... FAIL
  (url='http://127.0.0.1:8055/api/v1/pdf/lightship') ... FAIL
  (url='http://127.0.0.1:8055/api/v1/pdf/application-form') ... FAIL
  (url='http://127.0.0.1:8055/api/calculate') ... FAIL
test_07_extreme_numerical_values (__main__.TestAdversarialEndpoints.test_07_extreme_numerical_values)
Stress-test numerical boundaries: zero, negative, extreme large. ... ok
test_08_state_persistence_and_sync (__main__.TestAdversarialEndpoints.test_08_state_persistence_and_sync)
Verify initial-state, save-state, saved-state, and calculate roundtrips. ... ok
test_09_concurrent_burst_stress (__main__.TestAdversarialEndpoints.test_09_concurrent_burst_stress)
Fire 30 concurrent asynchronous requests to verify thread safety and responsiveness under burst load. ... ok

======================================================================
FAIL: test_06_null_fields_and_type_boundaries (url='http://127.0.0.1:8055/api/v1/pdf/detail-calc')
AssertionError: 500 == 500 : Unhandled 500 on /api/v1/pdf/detail-calc with null inputs!
======================================================================
FAIL: test_06_null_fields_and_type_boundaries (url='http://127.0.0.1:8055/api/v1/pdf/lightship')
AssertionError: 500 == 500 : Unhandled 500 on /api/v1/pdf/lightship with null inputs!
======================================================================
FAIL: test_06_null_fields_and_type_boundaries (url='http://127.0.0.1:8055/api/v1/pdf/application-form')
AssertionError: 500 == 500 : Unhandled 500 on /api/v1/pdf/application-form with null inputs!
======================================================================
FAIL: test_06_null_fields_and_type_boundaries (url='http://127.0.0.1:8055/api/calculate')
AssertionError: 500 == 500 : Unhandled 500 on /api/calculate with null inputs!
----------------------------------------------------------------------
Ran 9 tests in 61.047s
FAILED (failures=4)
```

### 1.2 Exact Traceback Isolation
**Command**:
```powershell
python -c "
import json, traceback
from app.services.calculation_service import CalculationService
with open('app/saved_state.json', 'r', encoding='utf-8') as f: state = json.load(f)
state['dashboard_inputs']['t_side'] = ''
CalculationService.compute_all_calculations(state)
"
```
**Verbatim Exception**:
```
Traceback (most recent call last):
  File "<string>", line 6, in <module>
    CalculationService.compute_all_calculations(state)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^
  File "E:\Bangla Scantling\app\services\calculation_service.py", line 340, in compute_all_calculations
    ls_data = LightshipService.calculate_lightship(state, plate_thk_map, is_single_hull)
  File "E:\Bangla Scantling\app\services\lightship_service.py", line 142, in calculate_lightship
    t_val = float(inputs[bound_k])
ValueError: could not convert string to float: ''
```

### 1.3 State Poisoning Verification
**Command**:
```powershell
python -c "
class DummyRepo:
    def get_raw_data(self): return {}
    def get_saved_state(self): return [1, 2, 3]

from app.services.state_service import StateService
svc = StateService(DummyRepo())
svc.get_initial_state()
"
```
**Verbatim Exception**:
```
Traceback (most recent call last):
  File "<string>", line 8, in <module>
    svc.get_initial_state()
    ~~~~~~~~~~~~~~~~~~~~~^^
  File "E:\Bangla Scantling\app\services\state_service.py", line 18, in get_initial_state
    for k, v in saved.items():
                ^^^^^^^^^^^
AttributeError: 'list' object has no attribute 'items'
```

---

## 2. Logic Chain

1. **Premise 1**: Web browsers submit empty strings `""` when users clear text fields in HTML forms.
2. **Observation 1**: `inputs.get(bound_k) is not None` in `app/services/lightship_service.py:141` evaluates to `True` when `inputs[bound_k] == ""`.
3. **Observation 2**: Line 142 invokes `float(inputs[bound_k])` without a `try/except` block or fallback default.
4. **Deduction 1**: Clearing any plate input (`t_keel`, `t_bottom`, `t_bilge`, `t_side`, `t_deck_hatch`, `t_bhd`) in the browser causes an uncaught `ValueError`.
5. **Observation 3**: FastAPI catches uncaught exceptions and converts them to HTTP `500 Internal Server Error`.
6. **Observation 4**: `app/api/v1/endpoints_state.py:34` receives raw JSON from requests and immediately calls `state_service.save_state(body)`.
7. **Observation 5**: `app/repositories/state_repository.py:59` writes the unvalidated JSON directly to disk at `app/saved_state.json`.
8. **Observation 6**: `app/services/state_service.py:18` iterates `for k, v in saved.items():` on the assumption that `saved` is a Python dictionary.
9. **Deduction 2**: Sending a non-dict JSON body (e.g., `[]`) to `POST /api/save-state` permanently disables `GET /api/initial-state` for all users by triggering an unhandled `AttributeError` on every subsequent request.
10. **Conclusion**: The API cannot be approved in its current state because common user actions (clearing form fields) and standard API stress scenarios result in unhandled 500 crashes and permanent server-wide denial of service.

---

## 3. Stress Test Results Matrix

| # | Test Scenario | Target Endpoints | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|---|
| 1 | Canonical GET Aliases | `/api/v1/pdf/*`, `/api/pdf/*` | 200 OK, valid PDF magic bytes, exact page counts (10, 2, 25) | 200 OK, 10/2/25 pages, valid PDF | **PASS** |
| 2 | Canonical POST Aliases | `/api/v1/pdf/*`, `/api/pdf/*` | 200 OK, valid PDF magic bytes, exact page counts (10, 2, 25) | 200 OK, 10/2/25 pages, valid PDF | **PASS** |
| 3 | CORS Preflight OPTIONS | `/api/v1/*`, `/api/*` across 6 origins | 200 OK, proper `Access-Control-Allow-*` headers | 200 OK with correct CORS headers | **PASS** |
| 4 | Empty JSON Body `{}` | All POST calculation & PDF endpoints | Graceful fallback to default/saved state, 200 OK | 200 OK with safe defaults | **PASS** |
| 5 | Partial State Payloads | `/api/calculate`, PDF endpoints | Evaluate supplied sections, fallback for missing | 200 OK, evaluated cleanly | **PASS** |
| 6 | Null Fields (`None`) | `/api/calculate`, PDF endpoints | Treat `None` as missing and use fallback baselines | 200 OK, fallback baselines used | **PASS** |
| 7 | Empty String `""` in Plate Inputs | `/api/calculate`, PDF endpoints | Graceful fallback to default baseline | **HTTP 500 (ValueError)** | **FAIL** |
| 8 | Non-numeric string (e.g. `"12mm"`) | `/api/calculate`, PDF endpoints | Graceful sanitization or 422 validation | **HTTP 500 (ValueError)** | **FAIL** |
| 9 | List JSON Body (`[1, 2, 3]`) | `POST /api/calculate` | 422 Unprocessable Entity or 400 Bad Request | **HTTP 500 (AttributeError)** | **FAIL** |
| 10 | Non-Dict Body Persistence | `POST /api/save-state` | 400 Bad Request rejecting invalid state structure | **Persisted corrupt JSON; broke /initial-state** | **FAIL** |
| 11 | Extreme Numerical Boundaries | Zero, Negatives, 100k m, 0.001 m | Compute without ZeroDivisionError or crash | 200 OK, stable math | **PASS** |
| 12 | High-Concurrency Burst Load | 32 parallel requests across 8 workers | Concurrent responses without deadlock or dropped connections | 200 OK, zero dropped requests | **PASS** |

---

## 4. Caveats

- **No Caveats**: All findings and observations are directly reproducible via the provided automated test script (`tests/adversarial_endpoint_stress.py`) and standalone command-line executions.
- **Review-Only Constraint Followed**: In accordance with the Challenger protocol, no implementation files in `app/` were modified by Challenger 1. Fixes must be implemented and verified by Worker 1.

---

## 5. Unchallenged Areas

- **Authentication & Authorization**: The application is an internal/statutory engineering tool operating without user authentication tokens; auth layers were not tested.
- **WebSocket Streaming**: The current system relies strictly on HTTP REST endpoints; no WebSockets are implemented.

---

## 6. Conclusion & Verdict

**Verdict**: **REJECT**

While Worker 1 successfully configured the route aliases, CORS middleware, and deliverable PDFs for nominal inputs, the implementation fails essential adversarial robustness requirements:
1. Form clearing or accidental unit annotations in browser inputs trigger unhandled `500 Internal Server Error` responses in `LightshipService.calculate_lightship`.
2. Lack of schema validation in `POST /api/save-state` enables persistent state corruption that disables `GET /api/initial-state`.
3. Lack of payload type checking in `POST /api/calculate` causes unhandled 500 crashes on non-dictionary bodies.

**Required Remediations before Approval**:
1. Implement safe `_to_float(val, default)` and `_to_int(val, default)` converters in `app/services/lightship_service.py` to prevent `ValueError` crashes on empty strings or non-numeric values.
2. Add dictionary type checks in `app/api/v1/endpoints_calculation.py` (`calculate_state`) and `app/api/v1/endpoints_state.py` (`save_state`).
3. Add defensive guarding in `StateService.get_initial_state()` (`if saved and isinstance(saved, dict):`).

---

## 7. Verification Method

To independently reproduce the failures:
```powershell
# 1. Run the comprehensive adversarial test harness
python tests/adversarial_endpoint_stress.py -v

# 2. Directly verify the empty string 500 crash
python -c "
import requests, json
with open('app/saved_state.json', 'r', encoding='utf-8') as f: state = json.load(f)
state['dashboard_inputs']['t_side'] = ''
r = requests.post('http://127.0.0.1:8055/api/calculate', json=state)
print('Status:', r.status_code, '(Expected 200/422, Got 500 crash)')
assert r.status_code != 500
"

# 3. Directly verify the non-dict calculate crash
python -c "
import requests
r = requests.post('http://127.0.0.1:8055/api/calculate', json=[1, 2, 3])
print('Status:', r.status_code, '(Expected 422, Got 500 crash)')
assert r.status_code != 500
"
```
