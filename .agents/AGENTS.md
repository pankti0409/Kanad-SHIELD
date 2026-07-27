# Custom Agent Rules for TraceVault

## Task Completion Rules
- **CRITICAL**: After the completion of every task, you must restart the TraceVault servers (both Backend and Frontend).
- **Restarting Backend Server**:
  - Kill any existing backend tasks if they are running.
  - Start the FastAPI backend server using the virtual environment Python interpreter:
    `venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
    in the directory `c:\Users\PANKTI\Desktop\Kanad SHIELD\tracevault\backend`.
- **Restarting Frontend Server**:
  - Kill any existing frontend tasks if they are running.
  - Start the Vite frontend server:
    `npx vite --host 0.0.0.0 --port 3000`
    in the directory `c:\Users\PANKTI\Desktop\Kanad SHIELD\tracevault\frontend`.
