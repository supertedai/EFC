# Options

## A. Relabel every present `settlement` object as a record

Replace “is settled” with a neutral phrase such as “settlement record present”. This removes the false claim but does not distinguish a waiting record from a completed outcome.

## B. Preserve contract presence and expose a typed status — selected

Keep the existing presence flag for compatibility/coverage, add a status derived from explicit completion fields, and render pending, completed, and incomplete/contract-only states distinctly. Unknown shapes remain non-settled rather than being promoted by a permissive fallback.

## C. Treat any non-empty `settlement` object as settled

Rejected: the measured EFC-fσ8 nodes directly falsify this interpretation; their settlement objects explicitly wait for DESI DR2 and the live arbiter header is `nei`.

## D. Change the EFC prediction, variant, or physical model

Rejected as out of scope and an owner-level scientific choice. This work changes only status representation and tests.