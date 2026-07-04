# Quiz Numberblock

Educational quiz web app (Spanish) for children: count objects or sum their values.

## Configuration

All game tuning is in `config.json`. Key settings:

| Key | Type | Description |
|---|---|---|
| `TOTAL_IMAGES` | int | Max image number available on disk (1.jpg to N.jpg). Used by sum/count games. |
| `GALLERY_CONTINUOUS_MAX` | int | Gallery shows 1..N continuously. Missing files display a placeholder. |
| `GALLERY_EXTRAS` | int[] | Additional numbers > N to include in the gallery. Only shown if the file exists on disk. |
| `SUM_MIN_VALUE` | int | Minimum value per sum image |
| `SUM_MAX_VALUE` | int | Maximum value per sum image |
| `SUM_TOTAL_MAX` | int | Maximum total sum allowed |
| `SUM_BIG_THRESHOLD` | int | If a summand exceeds this, the other is forced to small range |
| `SUM_SMALL_MIN` | int | Small range lower bound |
| `SUM_SMALL_MAX` | int | Small range upper bound (increases with streak > 20) |

### Gallery behavior

- Numbers 1 through `GALLERY_CONTINUOUS_MAX` are always shown. If an image file is missing, a placeholder SVG is displayed instead.
- Each number in `GALLERY_EXTRAS` is shown only if the corresponding `.jpg` or `.jpeg` file exists on disk.
- The full list is sorted numerically and paginated (50 per page).
- `TOTAL_IMAGES` and gallery settings are independent — changing gallery does not affect sum/count games.
