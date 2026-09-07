# Equal-assurance simpler workflow

`baseline.py` takes the identical model and query bytes through the same strict
decoder, one backend-adapter invocation, exact certificate checker, immutable
checked snapshot, and fresh fail-closed consumer check. It therefore has equal
assurance for the tested scope; it is not a deliberately weak straw baseline.

The baseline is clearer as an end-to-end script. The structured engine earns a
reusable producer/checker boundary for callers that need to store checked
artifacts or replace candidate-search backends. It does not earn better answers,
stronger mathematics, or a scalar score in this build.

