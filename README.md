# BIC21203 — Lab 4a: Client-Side Scripting (JavaScript)

**Name:** TAN YUE HENG
**Matric No:** AI240167
**Course:** BIC21203 Web Development
**Lab:** 4a — Client-Side Scripting (JavaScript)

---

## About this repository

This repository contains my solutions to the three Lab 4a JavaScript exercises. Each
question is a self-contained webpage built with plain HTML5, CSS and modern
JavaScript. **No external libraries or frameworks are used** — everything runs
directly in a current desktop browser.

The exercises cover functions, event handling with `addEventListener()`, input
validation with `if … else if … else`, a `for` loop, and DOM manipulation using
`createElement()` / `textContent` / `appendChild()`.

## Repository structure

```
Lab4a/
├── index.html            Landing page linking the three exercises
├── shared/
│   └── style.css         One shared stylesheet for all pages
├── q1/
│   ├── index.html        Question 1 — Interactive Text Changer
│   └── q1.js
├── q2/
│   ├── index.html        Question 2 — Smart Number Validator
│   └── q2.js
├── q3/
│   ├── index.html        Question 3 — Dynamic Number Generator
│   └── q3.js
├── screenshots/          Browser output evidence for each question
└── tests/                Automated browser tests (optional, not part of the site)
```

## How to run

1. Clone or download this repository.
2. Open `index.html` in Chrome, Edge or Firefox.
3. Choose an exercise, or open any question folder directly.

> No build step, server or installation is required. The pages are opened
> straight from the file system.

---

## Question 1 — Interactive Text Changer

Opens with the message *"Welcome to my website!"*. Clicking **Change Message**
replaces it with *"Hello there!"*.

**How it works** (`q1/q1.js`):

1. The paragraph and button are selected with `document.getElementById()`.
2. `changeMessage()` sets `message.textContent = "Hello there!"`.
3. The function is attached with `changeBtn.addEventListener("click", changeMessage)`.

`textContent` is used instead of `innerHTML` so text is always inserted as plain
text. No inline `onclick` attributes are used.

| Before | After |
|---|---|
| ![Q1 before](screenshots/q1_before.png) | ![Q1 after](screenshots/q1_after.png) |

---

## Question 2 — Smart Number Validator

Reads a number from the input and displays a validation message below it.

**How it works** (`q2/q2.js`):

`checkInput()` follows the required `if … else if … else` structure:

1. **Empty or whitespace-only** input → `"Please enter a valid number!"`.
   This is checked first because `Number("")` returns `0`, not `NaN`.
2. **Non-numeric** text (e.g. `abc`, `12px`) → `Number()` gives `NaN` →
   `"Please enter a valid number!"`.
3. **Below 10** → `"The number is lower than 10"`.
4. **Equal to 10** → `"The number is equal to 10"`.
5. **Otherwise** → `"The number is higher than 10"`.

The result is written to `#result` with `textContent` and announced through
`role="status"` / `aria-live="polite"`. The click is registered with
`addEventListener()`, and pressing Enter in the field also runs the check.

**Test results:**

| Input | Expected | Result | Screenshot |
|---|---|---|---|
| `5` | The number is lower than 10 | ✅ | [q2_lower](screenshots/q2_lower.png) |
| `15` | The number is higher than 10 | ✅ | [q2_higher](screenshots/q2_higher.png) |
| `10` | The number is equal to 10 | ✅ | [q2_equal](screenshots/q2_equal.png) |
| `abc` | Please enter a valid number! | ✅ | [q2_invalid](screenshots/q2_invalid.png) |
| *(empty)* | Please enter a valid number! | ✅ | [q2_empty](screenshots/q2_empty.png) |
| `10.5` | The number is higher than 10 | ✅ | [q2_decimal](screenshots/q2_decimal.png) |

Additional cases verified: `9.99` (lower), `-4` (lower), `0` (lower),
`12px` (invalid), and string of spaces (invalid).

---

## Question 3 — Dynamic Number Generator

Clicking **Generate** builds an ordered list containing
*"The number is 1"* through *"The number is 5"*.

**How it works** (`q3/q3.js`):

1. `generateNumbers()` is attached with `addEventListener("click", …)`.
2. `numberList.replaceChildren()` clears any existing items first, so repeated
   clicks never duplicate the list.
3. A `for` loop runs `for (let i = 1; i <= 5; i++)`.
4. Each item is created with `document.createElement("li")`, its text set with
   `textContent`, and appended with `appendChild()`.

| After one click | After four clicks (no duplicates) |
|---|---|
| ![Q3 generated](screenshots/q3_after.png) | ![Q3 repeated](screenshots/q3_repeat_clicks.png) |

---

## Testing summary

All three exercises were verified in a real browser using automated checks
(scripts live in `tests/`, not part of the submission site):

- **30 / 30 checks passed** across Q1, Q2 and Q3.
- Q2 was tested against 11 inputs including decimals, negatives and invalid text.
- Q3 was clicked four times to confirm the list stays at exactly 5 items.

To run the tests yourself (requires Python and Chrome):

```bash
python tests/test_lab4a.py
```

## Accessibility practices applied

- Descriptive `<label>` elements tied to inputs with `for` / `id`.
- Meaningful button text instead of "Click here".
- Visible status regions (`role="status"`, `aria-live="polite"`) so results are
  announced to screen reader users.
- `:focus-visible` outlines for keyboard navigation.
- `prefers-reduced-motion` respected by all animations.
