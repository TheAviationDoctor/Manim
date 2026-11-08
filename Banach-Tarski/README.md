A Manim Community Edition rendering of the 'infinite chocolate' optical illusion from [Vsauce (2015)](#references) (0:31–0:38).

## Rationale

Every chocolate facet is fixed geometry. The reassembly itself uses translations only (no morphing, scaling, crossfading, or changing the tile count on a piece). Integer-grid translations (3, 1) and (-1, 0) carry the extensions into the finished bar. All facets then match the original 4 x 8 grid exactly, while one square remains separate.

The deliberate trick is an overlap hidden underneath the bottom fragment. Both upper fragments extend a quarter-square below the visible diagonal before separation. Together those hidden extensions have area one square.

There is, alas, no such thing in life as free chocolate.

## Requisites

Requires Manim Community.
Does not require LaTeX or external assets.

## Render

With `uv`:
`uv run manim -pqh infinite_chocolate_manim.py InfiniteChocolate`

Without `uv`:
`manim -qh --format=mp4 infinite_chocolate_manim.py InfiniteChocolate`

## References

- Vsauce. (2015, July 31). The Banach–Tarski paradox [Video]. YouTube. https://www.youtube.com/watch?v=s86-Z-CbaHA