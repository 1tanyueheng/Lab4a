/* ==========================================================================
   Lab 4a - Question 1: Interactive Text Changer
   Tan Yue Heng | AI240167
   --------------------------------------------------------------------------
   Requirement:
     1. Select the paragraph and button using DOM selection methods.
     2. Define changeMessage() that replaces the paragraph text with "Hello there!".
     3. Attach the function to the button with addEventListener("click", ...).
   ========================================================================== */

"use strict";

/* ---------- 1. Select the elements with DOM selection methods ---------- */

/** The paragraph whose text will be replaced. */
const message = document.getElementById("message");

/** The button that triggers the change. */
const changeBtn = document.getElementById("changeBtn");

/** Status region that announces the result to assistive technology. */
const status = document.getElementById("status");

/* ---------- 2. The required function ---------- */

/**
 * Replace the paragraph text with the greeting.
 * Uses textContent (not innerHTML) so the text is inserted as plain text
 * and can never be interpreted as markup.
 */
function changeMessage() {
    const newText = "Hello there!";

    message.textContent = newText;

    // Restart the highlight animation each time the button is pressed.
    message.classList.remove("is-changed");
    // Reading offsetWidth forces the browser to reflow, which restarts the CSS animation.
    void message.offsetWidth;
    message.classList.add("is-changed");

    status.textContent = "Message changed to: \u201c" + newText + "\u201d";
}

/* ---------- 3. Attach the function with addEventListener ---------- */

changeBtn.addEventListener("click", changeMessage);
