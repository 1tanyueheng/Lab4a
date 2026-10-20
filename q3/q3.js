/* ==========================================================================
   Lab 4a - Question 3: Dynamic Number Generator
   Tan Yue Heng | AI240167
   --------------------------------------------------------------------------
   Requirement:
     - Define generateNumbers() and attach it with addEventListener().
     - Use a for loop that iterates from 1 through 5.
     - Create each <li> with document.createElement(), set its text with
       textContent, and append it to #numberList.
     - Clear existing items before generating again (no duplicates on repeat).
   ========================================================================== */

"use strict";

/* ---------- Element selection ---------- */
const generateBtn = document.getElementById("generateBtn");
const numberList = document.getElementById("numberList");
const status = document.getElementById("status");

/** How many numbers to generate. */
const START = 1;
const END = 5;

/**
 * Build the ordered list from 1 to 5.
 * The list is emptied first so repeated clicks never duplicate entries.
 */
function generateNumbers() {
    /*
       Clear existing items before generating again.
       replaceChildren() with no arguments removes every child in one step;
       it is the modern equivalent of list.innerHTML = "" (which would be unsafe
       for user content and is discouraged in this lab).
    */
    numberList.replaceChildren();

    /*
       For loop from 1 through 5 (inclusive).
       i goes 1, 2, 3, 4, 5 because the condition is i <= END.
    */
    for (let i = START; i <= END; i++) {
        // Create a new list item element
        const li = document.createElement("li");

        // Set its visible text safely
        li.textContent = "The number is " + i;

        // Append it to the ordered list
        numberList.appendChild(li);
    }

    // Announce the outcome in the status region
    status.textContent = "Generated " + numberList.children.length + " list items (1 to " + END + ").";
}

/* ---------- Event listener ---------- */
generateBtn.addEventListener("click", generateNumbers);
