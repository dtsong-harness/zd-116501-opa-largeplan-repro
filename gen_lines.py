# ZD-115407: generate a plan that renders >5000 SHORT lines (line-based cap),
# unlike the byte-heavy zd-116501 config. Mirrors iHerb's QuickSight for_each
# fan-out: many resources, many small attributes, each one plan line.
N_RES = 400   # resources
N_ATTR = 40   # short attributes each -> ~16,000 attribute lines + overhead
out = ['terraform {\n  required_version = ">= 1.5.0"\n}\n\n']
out.append('# Auto-generated for ZD-115407 line-volume repro (REPRO-20260701-001).\n')
out.append(f'# {N_RES} resources x {N_ATTR} short attrs => ~{N_RES*N_ATTR} plan lines,\n')
out.append('# well past the ~5000-line console viewing cap, with normal-sized lines\n')
out.append('# (no per-line 25KB truncation). Reproduces line-based truncation.\n\n')
for r in range(N_RES):
    out.append(f'resource "terraform_data" "grid_{r:04d}" {{\n  input = {{\n')
    for a in range(N_ATTR):
        out.append(f'    sheet_{a:02d} = "quicksight-analysis-r{r:04d}-visual-{a:02d}"\n')
    out.append('  }\n}\n\n')
open('main.tf','w').write(''.join(out))
print("wrote main.tf")
