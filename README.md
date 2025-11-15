# Отчет о выполнении задания по настройке Jenkins CI/CD

## Шаг 1: Генерация SSH ключей

### Выполненные команды:
```bash
cd secrets
ssh-keygen -t rsa -b 4096 -f jenkins_agent_ssh_key -N "" -C "jenkins-agent"
```

### Настройка прав доступа:
```bash
chmod 600 jenkins_agent_ssh_key
chmod 644 jenkins_agent_ssh_key.pub
```

### Результат:
- Создана пара SSH ключей: приватный (`jenkins_agent_ssh_key`) и публичный (`jenkins_agent_ssh_key.pub`)
- Установлены строгие права доступа для безопасности

## Шаг 2: Создание Dockerfile для SSH Agent

Создал файл `Dockerfile` со следующим содержимым:

```dockerfile
FROM jenkins/ssh-agent:latest

# Install PHP-CLI and dependencies
RUN apt-get update && \
    apt-get install -y \
    php-cli \
    php-curl \
    php-json \
    php-mbstring \
    php-xml \
    composer \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create agent directory
RUN mkdir -p /home/jenkins/agent
WORKDIR /home/jenkins/agent
```

### Особенности реализации:
- Использован официальный образ `jenkins/ssh-agent`
- Установлен полный набор PHP инструментов для работы с проектами
- Добавлен Composer для управления зависимостями
- Создана рабочая директория для агента

## Шаг 3: Создание docker-compose.yml

Разработал файл `docker-compose.yml` с учетом требования использования порта 8083:

```yaml
version: '3.8'

services:
  jenkins-controller:
    image: jenkins/jenkins:lts
    container_name: jenkins-controller
    ports:
      - "8083:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - ./secrets:/secrets:ro
    environment:
      - JENKINS_OPTS=--httpPort=8080
    networks:
      - jenkins-network

  ssh-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ssh-agent
    environment:
      - JENKINS_AGENT_SSH_PUBKEY=${JENKINS_AGENT_SSH_PUBKEY}
    volumes:
      - jenkins_agent_volume:/home/jenkins/agent
    depends_on:
      - jenkins-controller
    networks:
      - jenkins-network

volumes:
  jenkins_home:
  jenkins_agent_volume:

networks:
  jenkins-network:
    driver: bridge
```

### Ключевые моменты конфигурации:
- Порт 8083 проброшен на внутренний порт 8080 Jenkins
- Volume `jenkins_home` для сохранения данных Jenkins
- Volume `jenkins_agent_volume` для общего доступа к данным агента
- Сеть `jenkins-network` для изоляции контейнеров

## Шаг 4: Настройка переменных окружения

Создал файл `.env` для хранения публичного SSH ключа:

```bash
# Извлек публичный ключ и сохранил в переменную окружения
JENKINS_AGENT_SSH_PUBKEY=$(cat secrets/jenkins_agent_ssh_key.pub)
echo "JENKINS_AGENT_SSH_PUBKEY=${JENKINS_AGENT_SSH_PUBKEY}" > .env
```

## Шаг 5: Запуск контейнеров

### Сборка и запуск:
```bash
# Сборка образов
docker-compose build --no-cache

# Запуск контейнеров в фоновом режиме
docker-compose up -d
```

### Проверка статуса:
```bash
docker-compose ps
```
Результат:
```
NAME                 IMAGE                 COMMAND                  SERVICE              CREATED       STATUS          PORTS
jenkins-controller   jenkins/jenkins:lts   "/usr/bin/tini -- /u…"   jenkins-controller   2 hours ago   Up 12 seconds   0.0.0.0:50000->50000/tcp, :::50000->50000/tcp, 0.0.0.0:8083->8080/tcp, :::8083->8080/tcp
ssh-agent            jenkins-ssh-agent     "setup-sshd"             ssh-agent            2 hours ago   Up 2 hours      22/tcp
                              
```

## Шаг 6: Первоначальная настройка Jenkins Controller

### Получение initial admin password:
```bash
docker exec jenkins-controller cat /var/jenkins_home/secrets/initialAdminPassword
```

### Процесс настройки через веб-интерфейс:

1. **Открыл Jenkins в браузере:** http://localhost:8083
2. **Ввел полученный пароль администратора**
3. **Выбрал установку suggested plugins** - дождался завершения установки всех плагинов
4. **Создал административную учетную запись:**

## Шаг 7: Установка SSH Agent Plugin

### Действия в веб-интерфейсе:
1. Перешел в **Manage Jenkins** → **Manage Plugins**
2. Во вкладке **Available** нашел "SSH Agent Plugin"
3. Отметил плагин для установки и нажал **Install without restart**
4. Дождался успешной установки плагина

## Шаг 8: Настройка SSH Credentials в Jenkins

### Процесс добавления учетных данных:
1. **Manage Jenkins** → **Manage Credentials**
2. Нажал на домен **(global)**
3. **Add Credentials**:
   - Kind: `SSH Username with private key`
   - Scope: `Global`
   - ID: `jenkins-ssh-key`
   - Description: `SSH Key for Jenkins Agent`
   - Username: `jenkins`
   - Private Key: выбран `Enter directly`
   - В поле Key вставил содержимое приватного ключа из jenkins_agent_ssh_key

## Шаг 9: Создание и настройка Jenkins Agent

### Создание новой ноды:
1. **Manage Jenkins** → **Manage Nodes and Clouds** → **New Node**
2. Параметры ноды:
   - Node name: `ssh-agent1`
   - Type: `Permanent Agent`
   - Настройки:
     - Remote root directory: `/home/jenkins/agent`
     - Labels: `php-agent`
     - Usage: `Use this node as much as possible`
     - Launch method: `Launch agents via SSH`
     - Host: `ssh-agent`
     - Credentials: выбрал созданный `jenkins-ssh-key`
     - Host Key Verification Strategy: `Non verifying Verification Strategy`
     - Port: `22`

### Проверка подключения:
После сохранения настроек нода автоматически подключилась к контроллеру. Статус изменился с "Connecting" на "Connected".

## Шаг 10: Создание Jenkins Pipeline

### Создание Jenkinsfile:
Разработал `Jenkinsfile` с многостадийным пайплайном:

```groovy
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
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
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
    }
    
    post {
        always {
            echo 'Pipeline completed.'
        }
    }
}
```

### Создание Pipeline Job в Jenkins:
1. **New Item** → `php-project-pipeline`
2. Тип: `Pipeline`
3. Настройки:
   - Definition: `Pipeline script from SCM`
   - SCM: `Git`
   - Repository URL: `https://github.com/alexurx/php-project`
   - Script Path: `Jenkinsfile`

## Шаг 11: Тестирование системы

### Запуск пайплайна:
- Перешел в созданный job `php-project-pipeline`
- Нажал **Build Now**
- Наблюдал выполнение через **Console Output**

### Результаты выполнения:
- Все этапы выполнены успешно
- Агент `ssh-agent1` корректно использовался для выполнения задач
- Зависимости установлены успешно
- Тесты выполнены (для проектов с PHPUnit)

Результат:
- Jenkins доступен по http://localhost:8083
- Агент подключен и готов к работе
- PHP установлен и работает в контейнере агента

## Заключение

1. **Успешная настройка распределенной системы** с контроллером и агентом
2. **Корректная работа SSH соединения** между контейнерами
3. **Настройка пайплайна** для автоматической сборки PHP проектов

Система готова к использованию для автоматизации процессов CI/CD PHP проектов и может быть расширена дополнительными этапами пайплайна по мере необходимости.