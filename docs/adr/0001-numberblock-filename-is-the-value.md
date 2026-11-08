# Numberblock filenames encode their value

**Status:** accepted

## Context

The app serves numberblock images from a single flat `static/images/` directory and has no database or metadata file. Both the gallery and the sum quiz need to know the integer each image represents, and adding a number should not require a data migration.

## Decision

A numberblock for value `N` is stored as `N.jpg` or `N.jpeg` in `static/images/`. The filename is the only source of truth for the value; lookups prefer `.jpg` and then `.jpeg`. Missing files are tolerated: continuous gallery numbers fall back to a placeholder, and gallery extras are hidden.

## Consequences

- Adding an image asset is a file drop; making a new value reachable still requires raising the relevant config limit or adding it to the gallery extras.
- Renaming an image changes the value it represents.
- Duplicate `.jpg` and `.jpeg` files for the same value resolve to `.jpg`; the other is ignored.
- There is no place for metadata such as alt text, licensing, or difficulty, and nothing verifies that the image content matches the filename.
- A manifest or database would be needed if values become non-integer or require metadata.

## Considered options

An alternative is a JSON manifest or database. It is not used because it would duplicate the value and could drift from the files; the filename convention keeps one source of truth with no extra tooling.
