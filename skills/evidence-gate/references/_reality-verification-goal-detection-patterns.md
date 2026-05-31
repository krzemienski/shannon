# Goal-Detection Patterns

> Patterns for detecting whether a claimed "fix" / "implementation" / "completion" actually achieves the stated goal — vs. merely making the immediate symptom disappear.

## Why this matters

The most common implementation failure: a change that satisfies the LITERAL request without satisfying the UNDERLYING goal. The literal request was a proxy for what the user actually wanted; the proxy got optimized; the actual goal didn't.

Reality verification's job is to detect this gap. The patterns below name the recurring shapes.

## Pattern 1: Symptom-suppression vs. cause-fix

**Symptom-suppression**: the visible behavior changes but the underlying cause is untouched.

```
Goal: "Don't crash when the input is malformed."

Symptom-suppression fix:
  try:
      do_thing()
  except:
      pass

Cause-fix:
  if input_is_malformed(input):
      raise InputError(...)
  do_thing()
```

The symptom-suppression makes the crash go away. The error mode silently shifts to "produces wrong result without complaining." That's worse, not better.

**Detection:** for any try/except added in the diff, ask: "what was the actual fix?" If the answer is "the except clause," that's symptom suppression.

## Pattern 2: Test-targeted fix

**Test-targeted**: the fix is shaped around making a specific test pass, not around the underlying behavior.

```
Goal: "Function should return correct results for any valid input."

Test: assert f(5) == 10

Test-targeted fix:
  def f(x):
      if x == 5:
          return 10
      return original_logic(x)
```

The test passes. The function is now wrong for every input except 5. Reviewer who didn't read the diff carefully calls it shipped.

**Detection:** look for hard-coded values in the diff that match test inputs. Look for `if x == <specific value>` branches that weren't there before.

## Pattern 3: Scope-narrowing

**Scope-narrowing**: the original scope was too hard; the fix narrows scope without acknowledging the narrowing.

```
Goal: "Support uploading any image format."

Original implementation: handles PNG only.

"Fix": adds a check `if not is_png(img): reject(img)`.
```

The crash went away, but the goal isn't met — the system now refuses formats it was supposed to support. The user discovers this when they try JPEG.

**Detection:** look for new `if not <X>: reject` patterns where `X` is something the goal said to support. Look for documentation / error messages that newly restrict input.

## Pattern 4: Future-self deferral

**Future-self deferral**: the fix puts a TODO/FIXME that's never coming back.

```
Goal: "Auth tokens must refresh before expiration."

"Fix":
  # TODO: implement refresh logic
  return cached_token  # may be expired
```

This is sometimes intentional (an explicit deferral with a tracked issue), and sometimes a fig leaf. Detection requires looking at whether the TODO has a ticket attached.

**Detection:** grep for new TODO/FIXME/XXX/HACK comments. Check if any have ticket references. Untracked deferrals are usually NEVER-going-to-happen.

## Pattern 5: Test-the-test

**Test-the-test**: the fix changes the test instead of the code.

```
Goal: "Sum function should add numbers correctly."

Test that fails:  assert sum(2, 3) == 5
Code:             def sum(a, b): return a - b  # bug

"Fix" (wrong):
  assert sum(2, 3) == -1  # update test to match code
```

Yes, this happens. Detection requires asking: "did the test expectation change in the diff?"

**Detection:** grep diff for changes inside `assert` statements / test expectations. Validate that the new expectation matches the spec, not just the code.

## Pattern 6: Mock-instead-of-fix

**Mock-instead-of-fix**: when the real dependency is broken, mock it instead of fixing it.

```
Goal: "Test that the order processing works."

Broken: real Stripe API is down.

"Fix": replace Stripe call with mock_stripe.charge(...)
```

The test passes. The real code still calls the (now broken) Stripe API. Production fails differently than the test promised it wouldn't.

**Detection:** any new mock/stub introduced during validation work. Cross-check with `skills/no-mocking-validation-gates/`.

## Pattern 7: Configuration-driven escape

**Config escape**: the fix introduces a flag that makes the failing case configurable-off.

```
Goal: "Handle edge case X correctly."

"Fix":
  if config.ENABLE_X_HANDLING:
      handle_x()
  else:
      pass  # default

Config:
  ENABLE_X_HANDLING: false  # default
```

Now the failing case can be turned off. The bug still exists; it's just opted into. Reviewers who assume "default settings are correct" miss it.

**Detection:** new config flags that gate behavior. Especially flags with `ENABLE_*` / `DISABLE_*` / `SKIP_*` prefixes whose default value avoids the new behavior.

## Pattern 8: BEFORE/AFTER divergence

**BEFORE/AFTER divergence**: the BEFORE snapshot and AFTER snapshot show the bug visible before and visible after — just in a different shape.

Reality-verification's core technique: capture the state BEFORE the fix and AFTER the fix; compare. If the symptom moved without the underlying state actually changing, the fix is fake.

```
Goal: "Cart total should reflect discounts."

BEFORE: cart shows $100 (no discount applied)
AFTER:  cart shows $100 (still no discount; just the display label changed)
```

Both BEFORE and AFTER are wrong. The fix relabeled the screen; it didn't apply the discount.

**Detection:** ALWAYS capture BEFORE/AFTER state. Diff them deeply, not superficially.

## Pattern 9: Asymptote chase

**Asymptote chase**: each "fix" addresses 1 case; the next case fails the same way; never reaches generality.

```
Goal: "Handle Unicode input correctly."

Cycle 1: fix for é → works
Cycle 2: fails on 中 → fix for 中
Cycle 3: fails on 🎉 → fix for emoji
Cycle 4: fails on combining marks → fix for combining marks
...
```

Each cycle "works." None of them solves the underlying problem (which would be: use Unicode-aware operations throughout).

**Detection:** repeated fixes in the same area, each addressing one specific input. The pattern signals an architectural problem the iterative fixes can't reach.

## How reality-verification applies these

When validating a "fix is done" claim:

1. Run the BEFORE state capture
2. Apply the fix
3. Run the AFTER state capture
4. Diff BEFORE vs AFTER

Then check, for each pattern above:
- Symptom suppression? (try/except, except: pass)
- Test-targeted? (hard-coded values matching test inputs)
- Scope narrowing? (new rejection / validation that wasn't there)
- Future-self deferral? (untracked TODO)
- Test-the-test? (assertion changed in diff)
- Mock-instead-of-fix? (new mock/stub)
- Configuration escape? (new flag gating behavior)
- BEFORE/AFTER divergence? (state didn't actually change)
- Asymptote chase? (same-area fixes repeating)

Any pattern hit = NOT a real fix. Verdict FAIL, regardless of test status.

## Cross-references

- `skills/reality-verification/` — parent skill
- `references/mock-quality-checks.md` — sibling reference for mock detection
- `skills/no-mocking-validation-gates/` — overlaps with Pattern 6
- `skills/gate-validation-discipline/` — enforces "fix verified" Iron Rule
- `skills/root-cause-tracing/` — finds the underlying cause that fakes are avoiding
