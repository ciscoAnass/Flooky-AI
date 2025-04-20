# Claude Chatbot - University Project

A simple web-based chatbot powered by Anthropic's Claude API, created as a university project.

## Features

- Natural language conversation with Claude AI
- Conversation memory that maintains context
- Custom personality with emojis and friendly tone
- Responsive design for desktop and mobile devices
- Simple and intuitive user interface

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Anthropic Claude API
- **Deployment**: Microsoft Azure

## Project Structure

```
Flooky-AI/
│
├── app.py                  # Main application file
├── config.py               # Configuration settings
├── claude_service.py       # Claude API integration
├── conversation.py         # Conversation data handling
├── helpers.py              # Helper functions
│
├── static/
│   ├── css/
│   │   └── styles.css      # Main stylesheet
│   └── js/
│       └── chat.js         # Frontend JavaScript
│
├── templates/
│   ├── base.html           # Base template 
│   ├── index.html          # Chat interface page
│   └── about.html          # About page
│   ├── donation.html       # Donation page
│   └── contact.html        # Contact page
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Anthropic API key
- Microsoft Azure account (for deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/ciscoAnass/Flooky-AI
   cd Flooky-AI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your Anthropic API key.

5. Run the development server:
   
   ```bash
   python app.py
   ```

6. Open http://localhost:5000 in your browser.

### Deployment to Azure

1. Create an Azure Web App on the Azure portal (Linux, Python runtime).

2. Set up the pipeline in Azure DevOps with a YAML file:

Set up Azure Pipelines:

```go
trigger:
- main

pool:
  name: Default

variables:
  # Azure Web App name
  webAppName: 'Flooky-WebApp'
  # Azure Service Connection
  azureSubscription: 'SC-SlothAI'
  # Python version
  pythonVersion: '3.10'

stages:
- stage: Build
  displayName: 'Build stage'
  jobs:
  - job: BuildJob
    steps:
    # Use Python version
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
        addToPath: true
      displayName: 'Use Python $(pythonVersion)'
    
    # Install dependencies
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
      displayName: 'Install dependencies'
    
    # Create deployment artifacts
    - task: ArchiveFiles@2
      inputs:
        rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
        replaceExistingArchive: true
      displayName: 'Archive project files'
    
    # Publish build artifacts
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: '$(Build.ArtifactStagingDirectory)'
        artifactName: 'drop'
        publishLocation: 'Container'
      displayName: 'Publish artifacts'

- stage: Deploy
  displayName: 'Deploy stage'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: DeployJob
    displayName: 'Deploy to Azure Web App'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          # Deploy to Azure Web App
          - task: AzureWebApp@1
            inputs:
              azureSubscription: '$(azureSubscription)'
              appType: 'webAppLinux'
              appName: '$(webAppName)'
              package: '$(Pipeline.Workspace)/drop/$(Build.BuildId).zip'
              runtimeStack: 'PYTHON|3.10'
              startupCommand: 'pip install -r requirements.txt && pip install gunicorn && gunicorn --bind=0.0.0.0:8000 app:app'
            displayName: 'Deploy to Azure Web App'
```

3. Configure environment variables in the Azure portal (if needed).

4. Push your code to trigger the pipeline and deploy automatically.

## API Usage

This project uses the Anthropic Claude API. Make sure you have the appropriate API key and are following Anthropic's usage policies and rate limits.

## License

This project is created for educational purposes as part of a Studies assignment.
