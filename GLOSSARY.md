# Quiz Numberblock

A Spanish-language educational app where children explore numbers and practice addition with numberblocks. Canonical terms are Spanish, matching the interface; the English name is shown in parentheses when it differs.

## Language

### Numbers and gallery

**Número** (numberblock):
An image that represents one integer; the unit of both the gallery and the sum quiz.
_Avoid_: ficha, objeto, tarjeta, sticker

**Valor** (value):
The integer a numberblock represents. It is the gallery label and the summand in a sum quiz.
_Avoid_: cantidad, número (when the value is meant)

**Galería** (gallery):
The browsable catalog of numberblocks, ordered by value and split into pages.
_Avoid_: catálogo, biblioteca

**Rango continuo** (continuous range):
The numbers from 1 through the gallery's continuous maximum that are always shown, even when their image is missing.
_Avoid_: rango base, rango principal

**Extra de galería** (gallery extra):
A number outside the continuous range that is shown only when its image exists.
_Avoid_: número adicional, bonus

**Placeholder**:
The fallback illustration shown when a numberblock image is missing.
_Avoid_: imagen por defecto, dummy

### Play

**Suma** (sum quiz):
A quiz that shows one or more numberblocks and asks for the total of their values.
_Avoid_: ejercicio, problema

**Reto** (challenge):
A Suma variant in which the same numberblock value is repeated several times. It appears at streak milestones and awards two streak points.
_Avoid_: boss, jefe, bonus, nivel especial

**Hito** (milestone):
A positive streak value divisible by ten at which a Reto can appear. A failed Reto is not offered again at that hito; the next Reto normally comes at the following multiple of ten.
_Avoid_: checkpoint, boss milestone

**Racha** (streak):
The number of consecutive correct answers in a game type. A wrong answer leaves it unchanged, but three consecutive failures reset it to zero; a correct Reto adds two instead of one.
_Avoid_: estrellas, puntos, score

**Fallo consecutivo** (consecutive failure):
A wrong answer that counts toward resetting the racha. Three in a row reset both the racha and the failure count to zero.
_Avoid_: error, mistake

**Tipo de juego** (game type):
A quiz family with its own racha and failure count. Only Suma is active.
_Avoid_: modo, categoría

**Regla grande/pequeña** (big/small pairing):
A difficulty rule: when one numberblock's value is above the big threshold, the other must come from the small range so the total stays manageable.
_Avoid_: mezcla difícil, hard/easy pair

**Rango pequeño** (small range):
The allowed values for the companion numberblock in a big/small pairing. Its upper bound rises after racha 20 as the racha grows, up to the maximum numberblock value.
_Avoid_: rango fácil, números bajos

### Quiz anatomy

**Opciones** (options):
The answer choices of a quiz; exactly one is correct.
_Avoid_: respuestas, botones

**Distractor**:
An incorrect option close to the correct total, so the answer is not trivial.
_Avoid_: respuesta falsa, opción mala

**Total**:
The sum of the values shown in a Suma; the correct answer.
_Avoid_: resultado, suma (when the answer is meant)

**Último quiz** (last quiz):
The most recently served quiz in a session; the next submitted answer is verified against it.
_Avoid_: quiz actual, pregunta pendiente

### Session

**Sesión** (session):
The state of one browser: its racha, consecutive failures, último quiz, and challenge progress. There are no accounts or logins.
_Avoid_: usuario, cuenta, perfil

### Retired

**Conteo** (count):
The former quiz mode in which children counted a set of numberblocks. It was replaced by the Galería and is not part of the current product. See ADR-0003.
_Avoid_: count game (for current behavior)
