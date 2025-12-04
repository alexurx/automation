pipeline {
    agent { label 'ssh-agent' }
    stages {
        stage('Test') {
            steps { sh 'php -v' }
        }
    }
}
