# DevOps-final
GymNest is a Django gym exercise application designed to help users track and manage their gym exercises. It utilizes a MySQL database, a dataset sourced from Kaggle, and a CI/CD pipeline leveraging Jenkins, Docker, Kubernetes, and AWS.
## Features
* **Personalized Exercise Recommendations:**
    * Upon signup and login, users receive tailored exercise recommendations based on their self-selected fitness level (beginner, intermediate, expert).
    * The system dynamically suggests exercises to match the user's experience and goals.
* **Workout Calendar Management:**
    * Users can manage their workout schedules using an integrated calendar.
    * Users have the ability to add specific exercises to any day of their choosing.
    * This allows for flexible and structured workout planning.
* **Exercise Tracking:** Users can log their workouts, including sets, reps, and weights.
* **Kaggle Dataset Integration:** Pre-populated exercise data from a Kaggle dataset. https://www.kaggle.com/datasets/niharika41298/gym-exercise-data
* **User Authentication:** Secure user accounts for personalized tracking.
## Technologies Used
* **Backend:** Django (Python)
* **Database:** MySQL
* **Dataset:** Kaggle Fitness Dataset 
* **Containerization:** Docker, Docker Compose
* **CI/CD:** Jenkins, GitHub Actions
* **Infrastructure as Code:** Terraform
* **Cloud Platform:** AWS (ECR, EKS, EC2,S3,CloudFront,IAM)
* **Orchestration:** Kubernetes (EKS)
## Prerequisites
* AWS Account
* Terraform installed
* Docker and Docker Compose installed
* kubectl installed
* Jenkins installed and configured
* GitHub Account
* MySQL Server
## Quick Start (Local Development with Docker Compose)
To quickly run GymNest locally using Docker Compose, follow these steps:
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/faroukshtewee/DevOps-final.git
    ```
2.  **Open Docker Desktop:**
    * Ensure Docker Desktop is running on your system.
3.  **Change directory:**
    ```bash
    cd GymNest-final
    ```
4.  **Run Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    * This command will build the Docker images and start the application containers.
    * Once the containers are running, you can access the application in your browser at `http://localhost:8000`.
## Terraform Deployment (AWS Infrastructure)
To deploy the infrastructure on AWS using Terraform, follow these steps:
1.  **Change directory:**
    ```bash
    cd GymNest-final/terraform
    ```
2.  **Initialize Terraform:**
    ```bash
    terraform init
    ```
3.  **Validate Terraform configuration:**
    ```bash
    terraform validate
    ```
4.  **Plan the infrastructure changes:**
    ```bash
    terraform plan
    ```
5.  **Apply the infrastructure changes (This will create resources on your AWS account):**
    ```bash
    terraform apply
    ```
    * Ensure your AWS credentials are configured correctly before running these commands.
## Terraform Destroy (AWS Resource Removal)
To delete all the services and resources created by Terraform on AWS:
**Run Terraform destroy:**
    ```bash
    terraform destroy
    ```
## Generating Exercise Images
As the Kaggle dataset does not include images, an automated script has been developed to generate images for each exercise. To run this script:
1.  **Enter the Django container:**
    ```bash
    docker exec -it django-GymNest-container bash
    ```
2.  **Run the image generation script:**
    ```bash
    python -m exercisesApp.Automation.generate_images_automation
    ```
    * This script uses Selenium to automate interactions with https://raphaelai.org, generating and saving images for each exercise in your dataset.
## Stopping and Removing Docker Containers and Volumes
To stop and remove the Docker containers and volumes created by Docker Compose, use the following command:
```bash
docker-compose down -v
