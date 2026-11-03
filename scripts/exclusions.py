# Items dropped from the survey by scope rule, read by build_master.py and build_ledger.py.

# A claim about R is resolvable only through its position relative to 1, which shows as epidemic
# growth or decline. Any other value of R is latent, so checking it needs another model estimate.
R_VALUE={"D019","D024","D027","D032","D033","D034","D035","D036","D083","D095",
         "N032-a","N032-b","N074-b","N096-a","N096-b"}
R_VALUE_REASON="puts a value on R other than its position relative to 1"

EXCLUDE=R_VALUE
