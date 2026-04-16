# Transcript of AI Tool Usage

The instructions state that " if you use AI/Chatgpt for your project please include why and where you have used them and include what you learned along the process".  Thus, I have created this transcript to document my exact use of AI Sessions during the development of the ClassChat project. This transcript will include the specific prompts I used and the responses I received verbatim, and I will elaborate in the Technical Report how I applied the information provided by the AI to resolve issues and advance my project.

## Client-Server Communication Test Error Diagnosis and Resolution

User: The server launched without issue, but this error occured when attempting to lanch the client:

```
Traceback (most recent call last):
  File "C:\Users\rebec\OneDrive\Documents\GitHub\CMPS-413-001-Semester-Project-ClassChat-C00460817\ClassChatClient.py", line 5, in <module>
    clientSocket.connect((serverName,serverPort)) #Socket Connection
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
socket.gaierror: [Errno 11001] getaddrinfo failed
```

What is causing this error and how can it be resolved?

GitHub Copilot: The error message:

```
socket.gaierror: [Errno 11001] getaddrinfo failed
```

means that the client is trying to connect to a server using a hostname (`serverName`) that cannot be resolved to an IP address. This usually happens for one of these reasons:

### Causes

1. **Incorrect or undefined `serverName`:**  
   The variable `serverName` is either not set, set to an invalid value, or set to a hostname that does not exist.

2. **Typo in the hostname:**  
   There may be a spelling mistake in the server name.

3. **Network issues:**  
   The client cannot reach the DNS server to resolve the hostname.

### How to Resolve

1. **Check the value of `serverName`:**
   - Open ClassChatClient.py and look for the line where `serverName` is defined.
   - If you want to connect to a server running on your own machine, set `serverName = "localhost"` or `serverName = "127.0.0.1"`.

2. **Example fix:**
   ```python
   serverName = "localhost"  # or "127.0.0.1"
   serverPort = 12000        # (or whatever port your server is using)
   ```

3. **If using a remote server:**
   - Make sure the hostname is correct and reachable from your client machine.
   - Try pinging the hostname from your command prompt to verify connectivity.

4. **If `serverName` is being read from user input or a config file:**
   - Ensure the input or config value is correct and not empty.

### Summary

Set `serverName` to a valid hostname or IP address (e.g., `"localhost"` for local testing). This should resolve the `getaddrinfo failed` error. If you need help finding where `serverName` is set in your code, let me know!

---

