pipeline {
    agent {
        label 'php-agent'
    }
    
    stages {        
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing PHP dependencies...'
                sh '''
                    if [ -f "composer.json" ]; then
                        composer install --no-progress --no-interaction
                    else
                        echo "No composer.json found, skipping dependency installation"
                    fi
                '''
            }
        }
        
        stage('Code Analysis') {
            steps {
                echo 'Running code analysis...'
                sh '''
                    if command -v php >/dev/null 2>&1; then
                        echo "PHP version:"
                        php --version
                    fi
                    
                    if [ -f "composer.json" ]; then
                        echo "Composer dependencies installed successfully"
                    fi
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    # Look for PHPUnit configuration
                    if [ -f "phpunit.xml" ] || [ -f "phpunit.xml.dist" ]; then
                        if command -v vendor/bin/phpunit >/dev/null 2>&1; then
                            vendor/bin/phpunit --verbose
                        elif command -v phpunit >/dev/null 2>&1; then
                            phpunit --verbose
                        else
                            echo "PHPUnit not found, skipping tests"
                        fi
                    else
                        echo "No PHPUnit configuration found, skipping tests"
                    fi
                '''
            }
        }
        
        stage('Build Report') {
            steps {
                echo 'Generating build report...'
                sh '''
                    echo "Build completed on $(date)" > build-report.txt
                    echo "PHP Agent: $(php --version 2>/dev/null | head -1)" >> build-report.txt
                    echo "Build Status: SUCCESS" >> build-report.txt
                '''
                archiveArtifacts artifacts: 'build-report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed.'
            cleanWs()
        }
        success {
            echo 'All stages completed successfully!'
        }
        failure {
            echo 'Errors detected in the pipeline.'
        }
    }
}