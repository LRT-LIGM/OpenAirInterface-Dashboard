# GNodeB Implementation

## Implementation Description

The implementation uses a dedicated `GNodeB` class to manage the lifecycle and real-time log streaming of a gNodeB (gNB) process. This design centralizes process control and asynchronous stdout handling, making it easier to maintain and extend.

- The `GNodeB` class encapsulates starting, stopping, and status checking of the gNB process.
- The gNB’s stdout is asynchronously read line-by-line and pushed into an `asyncio.Queue` to enable real-time log streaming.
- A FastAPI WebSocket endpoint streams these logs live to connected clients.
- Separating process control and streaming logic improves code clarity and allows better error handling.

---

## Code Explanation

### `class GNodeB`

Represents a gNodeB instance, managing the associated subprocess and its stdout asynchronously.

- **Attributes :**  

    - `process`: Holds the subprocess.Popen instance of the running gNB.
    - `stdout_queue`: An `asyncio.Queue` buffering stdout lines from the gNB process.

- **Methods :**

     - `__init__()`  
    Initializes with no active process and an empty stdout queue.

     - `async start()`  
    Launches the gNB process using the specified executable and config file.  
    Checks that both files exist to avoid runtime errors.  
    Starts an asynchronous task `_stream_stdout_to_queue()` that reads stdout lines without blocking the event loop.

     - `async _stream_stdout_to_queue()`  
    Continuously reads stdout lines from the gNB process in a non-blocking way and enqueues them for consumption by WebSocket clients.

     - `stop()`  
    Stops the gNB process by sending a SIGTERM signal. Handles exceptions such as permission errors or process not running.

     - `is_running()`  
    Returns a boolean indicating if the gNB process is currently active.

---

### FastAPI Endpoints

- `@app.post("/gnb/start")`  
  Starts the gNB process by calling `gnb.start()`. Returns the PID if successful, or raises HTTP 500 with the error message.

- `@app.post("/gnb/stop")`  
  Stops the gNB process by calling `gnb.stop()`. Returns the stopped process PID or an HTTP error if the process is not running or cannot be stopped.

- `@app.websocket("/ws/gnb")`  
  WebSocket endpoint to stream gNB logs in real-time:   

    - Accepts the WebSocket connection.  
    - If the gNB is not running, immediately informs the client and closes the connection.  
    - Otherwise, continuously waits for new stdout lines from the queue with a timeout.  
    - Sends log lines to the client as they arrive.  
    - If the process ends or the client disconnects, the connection is closed.
