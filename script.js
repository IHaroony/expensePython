document.addEventListener('DOMContentLoaded', () => {
    const socket = io.connect('http://127.0.0.1:5000');

    // Initialize xterm.js with a custom font
    const term = new Terminal({
        cursorBlink: true,  // Make the cursor blink
        fontFamily: 'Cascadia Code, Courier New, monospace',
        fontSize: 15,
        theme: {
            background: 'rgba(255, 255, 255, 0.8)', // Semi-transparent background
            foreground: '#333', // Dark text color
            cursor: '#007ACC', // Light blue cursor
            selection: 'rgba(0, 120, 212, 0.3)', // Blue selection highlight
        }
    });

    // Open the terminal within the terminal container
    term.open(document.getElementById('terminal'));

    // Write the initial message to the terminal
    term.write("Press Enter to start the Expense Tracker...\r\n");

    let started = false;
    let userInput = '';

    // Handle terminal data (key presses)
    term.onData(data => {
        if (!started && data === '\r') {
            // User pressed Enter to start the tracker
            started = true;
            term.clear();
            socket.emit('start_code_execution');  // Start the tracker
        } else if (started) {
            if (data === '\r') {
                // User pressed Enter, send input to backend
                socket.emit('input', userInput);
                userInput = '';  // Clear the current input
                term.write('\r\n');  // Move to the next line
            } else {
                // Collect user input
                userInput += data;
                term.write(data);  // Echo input to the terminal
            }
        }
    });

    // Listen for backend output and display it in the terminal
    socket.on('output', (data) => {
        term.write(data + '\r\n');  // Display backend output in the terminal
    });
});
