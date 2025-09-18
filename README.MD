
### Setting Up Your Development Environment

1.  **Fork the repository** by clicking the "Fork" button on the [main repository page](https://github.com/sivakumar232/timetable-server).

2.  **Clone your fork** to your local machine:
    ```bash
    git clone [https://github.com/YOUR-USERNAME/timetable-server.git](https://github.com/YOUR-USERNAME/timetable-server.git)
    cd timetable-server
    ```

3.  **Create a Virtual Environment**. It's a best practice to work in a virtual environment to manage dependencies.
    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (on Windows)
    .\venv\Scripts\activate

    # Activate it (on MacOS/Linux)
    source venv/bin/activate
    ```

4.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Add the `upstream` remote** to keep your fork synced with the main project:
    ```bash
    git remote add upstream [https://github.com/sivakumar232/timetable-server.git](https://github.com/sivakumar232/timetable-server.git)
    ```

### Making Changes and Submitting a Pull Request

1.  **Sync your `develop` branch** with the main project:
    ```bash
    # Switch to your local develop branch
    git checkout develop

    # Pull the latest changes from the main project's develop branch
    git pull upstream develop
    ```

2.  **Create a new feature branch** from `develop`:
    ```bash
    # Use a descriptive branch name (e.g., 'feat/optimize-fitness-function')
    git checkout -b your-new-feature-branch
    ```

3.  **Make your code changes**. Write clean, readable code and add comments where necessary.

4.  **Commit and push your changes** to your fork:
    ```bash
    git add .
    git commit -m "feat: A brief description of your new feature or fix"
    git push -u origin your-new-feature-branch
    ```

5.  **Open a Pull Request (PR)**.
    - Go to your fork on GitHub.
    - Click the "Compare & pull request" button.
    - **Important**: Ensure the target is the `develop` branch of the `sivakumar232/timetable-server` repository.
    - Write a clear title and description for your PR, explaining the changes you made.
    - Click "Create pull request".

The maintainers will review your submission and provide feedback. Thank you for your contribution!

