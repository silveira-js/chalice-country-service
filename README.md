# AWS Chalice-Based Country Data Service

## Project Overview

This project is a serverless application built using AWS Chalice that provides a service for retrieving, storing, and serving country data from an external API. The application demonstrates best practices for cost-efficiency and scalability in the AWS cloud environment.

## Architecture Description

The application uses the following AWS services:

- AWS Lambda: Runs the serverless functions
- Amazon API Gateway: Manages the API endpoints
- Amazon DynamoDB: Stores country data and operation statuses
- Amazon ElastiCache (Redis): Implements rate limiting
- AWS SQS: For asynchronous processing of data fetching
- AWS CodePipeline and CodeBuild: For CI/CD
- Amazon CloudWatch: For monitoring and alerting

The application is built using the AWS Chalice framework, which simplifies the development and deployment of serverless applications on AWS.

## Key Features

1. Asynchronous data fetching using SQS
2. Rate limiting with Redis
3. Continuous Integration and Deployment (CI/CD) pipeline
4. Comprehensive monitoring and alerting
5. Infrastructure as Code (IaC) using Terraform

## Setup Instructions

### Prerequisites

- AWS CLI installed and configured
- Terraform installed
- Python 3.8 or higher
- Git
- pyenv (for Python version management)

### Initial Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/country-data-service.git
   cd country-data-service
   ```

2. Set up Python environment using pyenv:
   ```
   pyenv install 3.8.0  # or your preferred Python version
   pyenv local 3.8.0
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Create an S3 bucket and DynamoDB table for Terraform state:
   ```
   ./create_terraform_state_bucket.sh
   ```

4. Update the `backend.tf` file with the correct bucket name if you chose a different name.

### Setting up GitHub Connection in AWS

Before deploying the infrastructure, you need to set up a connection between AWS and your GitHub repository. This is necessary for the CI/CD pipeline to access your code.

1. Go to the AWS CodePipeline console.

2. In the navigation pane, choose Settings, then choose Connections.

3. Choose Create connection.

4. For Provider, choose GitHub.

5. Choose Connect to GitHub.

6. If prompted, authenticate with your GitHub credentials.

7. When asked to Install a new app, choose the GitHub account where you want to install the AWS Connector for GitHub.

8. Choose the repository you want to connect to AWS.

9. Review the permissions and choose Connect.

10. Name your connection and choose Create connection.

11. Once the connection is created, note down the ARN of the connection.

12. Update the `github_connection_arn` variable in your `dev.tfvars` file with this ARN.

### Deployment

1. Initialize Terraform:
   ```
   cd terraform
   terraform init
   ```

2. Plan the infrastructure:
   ```
   make plan-infra
   ```

3. Apply the infrastructure:
   ```
   make apply-infra
   ```

4. The CI/CD pipeline will automatically deploy the Chalice application.

## API Documentation

### 1. Fetch Country Data

- **Endpoint**: `GET /fetch/{country}`
- **Description**: Triggers asynchronous data fetching for a specific country
- **Format**: Use dashes (-) for multi-word country names (e.g., 'united-states', 'costa-rica')

### 2. Get Country Data

- **Endpoint**: `GET /country/{country}`
- **Description**: Retrieves stored data for a country

### 3. Check Operation Status

- **Endpoint**: `GET /status/{country}`
- **Description**: Checks the status of data retrieval operations

## Key Design Decisions and Trade-offs

1. **Asynchronous Processing**: Implemented using SQS for better scalability and reliability. This allows for handling potentially time-consuming operations without blocking the API response.

2. **DynamoDB for Storage**: Chosen for its scalability and serverless nature. Trade-off: Potential increased costs for high-volume applications compared to traditional databases.

3. **Rate Limiting**: Implemented using Redis for distributed rate limiting. This allows for consistent rate limiting across multiple Lambda instances.

4. **CI/CD Pipeline**: Automated deployment process using CodePipeline and CodeBuild. This ensures consistent and reliable deployments but adds complexity to the infrastructure.

5. **Infrastructure as Code**: Using Terraform for infrastructure management. This provides version control and reproducibility for the infrastructure but requires additional learning and maintenance.

6. **Monitoring and Alerting**: Comprehensive CloudWatch alarms for various metrics. This provides good observability but may incur additional costs.

## Testing

The project includes unit tests for the main components. To run the tests:

```
cd country-data-service
python -m pytest
```

## Security Considerations

1. Rate limiting implemented using Redis to protect against API abuse.
2. Encryption at rest for DynamoDB using AWS-managed keys (SSE-AES-256).
3. Input validation and sanitization for country names to prevent injection attacks.
4. SQS queue configured with server-side encryption.
5. S3 bucket for Chalice state store configured with server-side encryption (AES-256).
6. Proper IAM roles and policies for least privilege access.

## Cost Optimization Strategies

1. Serverless architecture (AWS Lambda) to minimize idle resource costs.
2. DynamoDB configured with provisioned capacity for predictable workloads.
3. Rate limiting with Redis to reduce the risk of unexpected high costs due to API abuse.
4. Asynchronous processing using SQS to manage data fetching and processing rates.
5. CloudWatch alarms for monitoring various metrics to identify cost-related issues early.
6. NAT Gateways in the VPC setup to optimize costs for outbound internet traffic from private subnets.

## Potential Future Improvements

1. Implement diverse search parameters (e.g., country code, full/partial name)
2. Add Redis caching for frequently accessed country data
3. Support bulk operations for multiple countries
4. Extend API with additional search criteria (e.g., capital, population range, continent)

## Conclusion

This AWS Chalice-based Country Data Service demonstrates a scalable, cost-efficient, and maintainable serverless architecture for retrieving and serving country data. By leveraging AWS services and following best practices, the application provides a solid foundation for further development and optimization in a production environment.