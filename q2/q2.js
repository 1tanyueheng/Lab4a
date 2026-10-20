/* ==========================================================================
   Lab 4a - Question 2: Smart Number Validator
   Tan Yue Heng | AI240167
   --------------------------------------------------------------------------
   Requirement:
     - Read the input; treat empty / whitespace-only as invalid.
     - Convert a valid numeric string to a number and detect non-numeric values.
     - Use an if ... else if ... else structure to compare against 10.
     - Write the message into #result with textContent.
     - Register the click with addEventListener().
   ========================================================================== */

"use strict";

/* ---------- Element selection ---------- */
const userInput = document.getElementById("userInput");
const checkBtn = document.getElementById("checkBtn");
const resetBtn = document.getElementById("resetBtn");
const result = document.getElementById("result");

/**
 * Show a message in the result region and apply a colour modifier class.
 * @param {string} text  - the message to display
 * @param {string} state - one of: valid, low, high, equal, invalid
 */
function showResult(text, state) {
    result.textContent = text;

    // Replace any previous state class so colours never stack up.
    result.classList.remove("is-valid", "is-low", "is-high", "is-equal", "is-invalid");
    result.classList.add("is-" + state);
}

/**
 * Validate the input and display the outcome.
 * The comparison is a straightforward if / else if / else chain:
 *   1. invalid input
 *   2. lower than 10
 *   3. equal to 10
 *   4. otherwise (higher than 10)
 */
function checkInput() {
    const raw = userInput.value;
    const trimmed = raw.trim();

    /* --- Case 1: empty or whitespace only --- */
    if (trimmed === "") {
        showResult("Please enter a valid number!", "invalid");
        return;
    }

    /*
       Convert to a number.
       Number() returns NaN for things like "abc" or "12px".
       NOTE: Number("") is 0, which is why the empty check is done first.
    */
    const value = Number(trimmed);
    const isNumeric = !Number.isNaN(value);

    if (!isNumeric) {
        /* Token was present but is not a number */
        showResult("Please enter a valid number!", "invalid");
    } else if (value < 10) {
        showResult("The number is lower than 10", "low");
    } else if (value === 10) {
        showResult("The number is equal to 10", "equal");
    } else {
        showResult("The number is higher than 10", "high");
    }
}

/* ---------- Event listeners ---------- */

// Main action: the Check button.
checkBtn.addEventListener("click", checkInput);

// Convenience: pressing Enter inside the field also checks the value.
userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        checkInput();
    }
});

// Clear button resets the field, the message and returns focus to the input.
resetBtn.addEventListener("click", function () {
    userInput.value = "";
    result.textContent = "";
    result.classList.remove("is-valid", "is-low", "is-high", "is-equal", "is-invalid");
    userInput.focus();
});
