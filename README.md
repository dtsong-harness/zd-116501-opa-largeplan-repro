# Large-plan Terraform for REPRO-20260626-037 (ZD-116501)

Reproduces the IaCM OPA large-file skip threshold: a Terraform plan whose
`plan_human` artifact exceeds 100 MB, the point at which
`IACM_ENABLE_LARGEFILE_SKIP_OPA` makes the plugin skip the OPA evaluation
upload instead of failing.

## What it does

`main.tf` declares 190 `terraform_data` resources (builtin provider, no cloud
credentials, no real infrastructure), each with 24 attributes carrying a ~24k
character filler string. The plan diff renders the resolved value for every
attribute, so the text plan (`plan_human`) balloons to ~109.6 MB. This mirrors
iHerb's failing run (114,149,006 bytes, "using full structs in
stripIrrelevantDrift").

`terraform_data` is used (not `null_resource` or a cloud resource) so the plan
runs anywhere with zero provider auth and creates nothing on apply.

## Calibrated size

| Source `main.tf` | `tofu show` plan_human | `tofu show -json` |
|------------------|------------------------|-------------------|
| 198 KiB          | ~109.6 MB              | ~363 MiB          |

Measured locally with OpenTofu v1.12.0:

```bash
tofu init && tofu plan -out=plan.bin
tofu show -no-color plan.bin | wc -c   # ~109,637,652 bytes
```

## Regenerating / retuning the size

`gen.py count attrs_per_resource chars_per_attr` regenerates `main.tf`. The
filler is defined once as a local and reused, so the source stays small while
the plan stays huge. Rough knob: plan_human bytes ≈ count × attrs × chars.

```bash
python3 gen.py 190 24 24000 > main.tf   # ~110 MB (default, matches iHerb)
python3 gen.py 60 24 24000  > main.tf   # ~35 MB (30-100 MB band: plan FAILS, no skip)
python3 gen.py 50 24 24000  > main.tf   # ~29 MB (just under 30 MB: OPA 500s)
```

Note `range()` is capped at 1024 in OpenTofu/Terraform; the filler is built
from a 100-char base chunk repeated `chars/100` times to stay under that cap.

## A/B reproduction design (ZD-116501)

Same ~110 MB plan, two flag states on account `1RBryjuNSraDUqzkDUIiAw`:

1. **Flag OFF** (baseline): expect the plan step to fail uploading `plan_human`
   with `error uploading data 'plan_human' to Harness: ErrorResponse` (iHerb's
   symptom).
2. **Flag ON** (`IACM_ENABLE_LARGEFILE_SKIP_OPA`, confirmed enabled via direct
   target override on Prod1): expect OPA evaluation to be skipped and the
   `policyEvaluationStatus_plan_human` output variable to fire. Capture its
   exact value spelling (skipped vs evaluated/executed).
