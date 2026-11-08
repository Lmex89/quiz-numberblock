# The count game is retired in favor of the gallery

**Status:** accepted

## Context

The product originally offered two quiz modes: Count and Sum. Count presented a set of images for the child to count. The gallery was later introduced as a browsable catalog of numbers, showing the numberblocks and their labels.

## Decision

Count is no longer an active product mode. The home screen offers Galería (explore numbers) and Suma (practice addition), and the backend exposes no count quiz endpoint. Residual count names in session state, configuration defaults, and `count.js` are legacy and do not describe current behavior.

## Consequences

- Count streak and failure fields can exist in old sessions but are never updated.
- `count.js` is the gallery script; the name is historical.
- Reintroducing Count is a new product decision and endpoint, not a bug fix.
