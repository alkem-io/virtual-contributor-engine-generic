# Data Model: speckit-init

No new data entities are introduced. This feature adds development infrastructure only.

## Configuration Entities

### CI Environment Variables
Required env vars for CI (set in workflow, not in code):
- LOG_LEVEL: INFO
- RABBITMQ_HOST: localhost (test default)
- RABBITMQ_USER: guest
- RABBITMQ_PASSWORD: guest
- RABBITMQ_QUEUE: test
- RABBITMQ_RESULT_QUEUE: test-result

### Flake8 Configuration
- max-line-length: 100
- exclude: .git,__pycache__,.specify
