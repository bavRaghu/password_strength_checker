pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'bavyaraghu/password-strength-checker'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install and Selenium Tests') {
            steps {
                bat '''
                    @echo off
                    if not exist .venv py -m venv .venv
                    call .venv/Scripts/activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    python -m compileall -q app.py
                    python -m unittest -v test_app
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    @echo off
                    docker build -t "%IMAGE_NAME%:%IMAGE_TAG%" -t "%IMAGE_NAME%:latest" .
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    bat '''
                        @echo off
                        powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:DOCKERHUB_TOKEN | docker login -u $env:DOCKERHUB_USER --password-stdin; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
                        if errorlevel 1 exit /b 1
                        docker push "%IMAGE_NAME%:%IMAGE_TAG%"
                        if errorlevel 1 exit /b 1
                        docker push "%IMAGE_NAME%:latest"
                        if errorlevel 1 exit /b 1
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat '''
                    @echo off
                    powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content 'k8s/deployment.yaml' -Raw).Replace('IMAGE_PLACEHOLDER', ($env:IMAGE_NAME + ':' + $env:IMAGE_TAG)) | kubectl apply -f -; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
                    if errorlevel 1 exit /b 1
                    kubectl apply -f k8s/service.yaml
                    if errorlevel 1 exit /b 1
                    kubectl rollout status deployment/password-strength-checker --timeout=180s
                    if errorlevel 1 exit /b 1
                '''
            }
        }
    }

    post {
        always {
            bat 'docker image prune -f'
        }
    }
}
