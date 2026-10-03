const taskSelect = document.getElementById("task");

const userInput = document.getElementById("user-input");

const levelContainer = document.getElementById("level-container");
const goalContainer = document.getElementById("goal-container");

const levelSelect = document.getElementById("level");
const goalInput = document.getElementById("goal");

const submitButton = document.getElementById("submit-button");

const buttonText = document.getElementById("button-text");
const loadingText = document.getElementById("loading");

const resultCard = document.getElementById("result-card");
const resultContainer = document.getElementById("result");

const clearButton = document.getElementById("clear-button");


// ---------------------------------------------------------
// Task configuration
// ---------------------------------------------------------

const taskConfig = {
    qa: {
        label: "Enter your question",
        placeholder: "Example: What is HTML?",
        button: "Generate Answer"
    },

    explain: {
        label: "Enter the concept",
        placeholder: "Example: Explain JavaScript functions",
        button: "Explain Concept"
    },

    quiz: {
        label: "Enter the quiz topic",
        placeholder: "Example: Python basics",
        button: "Generate Quiz"
    },

    summarize: {
        label: "Enter the text to summarize",
        placeholder: "Paste the text you want to summarize here...",
        button: "Summarize Text"
    },

    learning: {
        label: "Enter the learning topic",
        placeholder: "Example: Web Development",
        button: "Create Learning Path"
    }
};


// ---------------------------------------------------------
// Change input fields according to selected task
// ---------------------------------------------------------

taskSelect.addEventListener("change", updateTaskUI);


function updateTaskUI() {

    const selectedTask = taskSelect.value;

    const config = taskConfig[selectedTask];

    if (!config) {
        return;
    }


    // Update label
    const inputLabel = document.querySelector(
        'label[for="user-input"]'
    );

    inputLabel.textContent = config.label;


    // Update placeholder
    userInput.placeholder = config.placeholder;


    // Update button text
    buttonText.textContent = config.button;


    // Show level for explanation, quiz and learning path
    if (
        selectedTask === "explain" ||
        selectedTask === "quiz" ||
        selectedTask === "learning"
    ) {

        levelContainer.classList.remove("hidden");

    } else {

        levelContainer.classList.add("hidden");

    }


    // Show goal only for learning path
    if (selectedTask === "learning") {

        goalContainer.classList.remove("hidden");

    } else {

        goalContainer.classList.add("hidden");

    }
}


// ---------------------------------------------------------
// Submit
// ---------------------------------------------------------

submitButton.addEventListener(
    "click",
    handleSubmit
);


async function handleSubmit() {

    const task = taskSelect.value;

    const input = userInput.value.trim();

    const level = levelSelect.value;

    const goal = goalInput.value.trim();


    if (!input) {

        showResult(
            "Please enter something before generating a result.",
            true
        );

        return;
    }


    setLoading(true);


    try {

        let response;


        // -------------------------------------------------
        // Q&A
        // -------------------------------------------------

        if (task === "qa") {

            response = await fetch("/qa", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: input
                })

            });

        }


        // -------------------------------------------------
        // Explanation
        // -------------------------------------------------

        else if (task === "explain") {

            response = await fetch("/explain", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    topic: input,
                    level: level
                })

            });

        }


        // -------------------------------------------------
        // Quiz
        // -------------------------------------------------

        else if (task === "quiz") {

            response = await fetch("/quiz", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    topic: input,
                    level: level
                })

            });

        }


        // -------------------------------------------------
        // Summary
        // -------------------------------------------------

        else if (task === "summarize") {

            response = await fetch("/summarize", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text: input
                })

            });

        }


        // -------------------------------------------------
        // Learning Path
        // -------------------------------------------------

        else if (task === "learning") {

            response = await fetch(
                "/learn/recommendations",
                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        topic: input,
                        level: level,
                        goal: goal || "Learn the topic"
                    })

                }
            );

        }


        if (!response) {

            throw new Error(
                "Invalid task selected."
            );

        }


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Something went wrong."
            );

        }


        displayResult(task, data);

    }

    catch (error) {

        showResult(
            error.message,
            true
        );

    }

    finally {

        setLoading(false);

    }
}


// ---------------------------------------------------------
// Display result
// ---------------------------------------------------------

function displayResult(task, data) {

    resultCard.classList.remove("hidden");


    // Q&A
    if (task === "qa") {

        resultContainer.innerHTML = `
            <div class="result-section">
                <h3>Answer</h3>
                <p>${escapeHTML(data.answer)}</p>
            </div>
        `;

    }


    // Explanation
    else if (task === "explain") {

        resultContainer.innerHTML = `
            <div class="result-section">
                <h3>Explanation</h3>
                <p>${escapeHTML(data.explanation)}</p>
            </div>
        `;

    }


    // Quiz
    else if (task === "quiz") {

        let html = `
            <div class="result-section">
                <h3>${escapeHTML(data.topic)}</h3>
        `;


        data.questions.forEach(
            (question, index) => {

                html += `
                    <div class="quiz-question">

                        <h4>
                            ${index + 1}.
                            ${escapeHTML(question.question)}
                        </h4>

                        <div class="quiz-options">
                `;


                question.options.forEach(
                    (option) => {

                        html += `
                            <div class="quiz-option">
                                ${escapeHTML(option)}
                            </div>
                        `;

                    }
                );


                html += `
                        </div>

                        <p class="correct-answer">
                            <strong>Correct Answer:</strong>
                            ${escapeHTML(question.correct_answer)}
                        </p>

                        <p>
                            <strong>Explanation:</strong>
                            ${escapeHTML(question.explanation)}
                        </p>

                    </div>
                `;

            }
        );


        html += `
            </div>
        `;


        resultContainer.innerHTML = html;

    }


    // Summary
    else if (task === "summarize") {

        resultContainer.innerHTML = `
            <div class="result-section">
                <h3>Summary</h3>
                <p>${escapeHTML(data.summary)}</p>
            </div>
        `;

    }


    // Learning Path
    else if (task === "learning") {

        let html = `
            <div class="result-section">

                <h3>
                    ${escapeHTML(data.topic)}
                </h3>

                <p>
                    <strong>Goal:</strong>
                    ${escapeHTML(data.goal)}
                </p>
        `;


        data.stages.forEach(
            (stage, index) => {

                html += `
                    <div class="learning-stage">

                        <h4>
                            Stage ${index + 1}:
                            ${escapeHTML(stage.stage)}
                        </h4>

                        <p>
                            <strong>Timeline:</strong>
                            ${escapeHTML(stage.timeline)}
                        </p>

                        <h5>Topics</h5>

                        <ul>
                `;


                stage.topics.forEach(
                    (topic) => {

                        html += `
                            <li>
                                ${escapeHTML(topic)}
                            </li>
                        `;

                    }
                );


                html += `
                        </ul>

                        <h5>Resources</h5>

                        <ul>
                `;


                stage.resources.forEach(
                    (resource) => {

                        html += `
                            <li>
                                ${escapeHTML(resource)}
                            </li>
                        `;

                    }
                );


                html += `
                        </ul>

                    </div>
                `;

            }
        );


        html += `
            </div>
        `;


        resultContainer.innerHTML = html;

    }


    // Scroll to result
    resultCard.scrollIntoView({
        behavior: "smooth"
    });
}


// ---------------------------------------------------------
// Error/result message
// ---------------------------------------------------------

function showResult(message, isError = false) {

    resultCard.classList.remove("hidden");

    resultContainer.innerHTML = `
        <div class="${isError ? "error-message" : "result-section"}">
            <p>${escapeHTML(message)}</p>
        </div>
    `;

    resultCard.scrollIntoView({
        behavior: "smooth"
    });
}


// ---------------------------------------------------------
// Loading state
// ---------------------------------------------------------

function setLoading(isLoading) {

    submitButton.disabled = isLoading;

    if (isLoading) {

        buttonText.classList.add("hidden");
        loadingText.classList.remove("hidden");

    } else {

        buttonText.classList.remove("hidden");
        loadingText.classList.add("hidden");

    }
}


// ---------------------------------------------------------
// Clear result
// ---------------------------------------------------------

clearButton.addEventListener(
    "click",
    () => {

        resultContainer.innerHTML =
            "Your result will appear here.";

        resultCard.classList.add("hidden");

    }
);


// ---------------------------------------------------------
// Basic HTML escaping
// ---------------------------------------------------------

function escapeHTML(value) {

    const div = document.createElement("div");

    div.textContent = String(value ?? "");

    return div.innerHTML;
}


// ---------------------------------------------------------
// Initialize UI
// ---------------------------------------------------------

updateTaskUI();