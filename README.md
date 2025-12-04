 Отчет по Индивидуальной Работе IW05: Автоматизация Конфигурации Сервера с Использованием Ansible и Jenkins

## 1. Описание Проекта

Данный проект (Лабораторная работа 5) является продолжением предыдущих индивидуальных работ и нацелен на освоение инструментов для **Configuration Management** и **Continuous Delivery**. Мы создали комплексную CI/CD среду, используя **Docker** и **Docker Compose** для изоляции сервисов.

**Ключевые цели:**

1. Установка и настройка Jenkins Controller.
    
2. Создание специализированных агентов (SSH Agent для сборки PHP, Ansible Agent для управления инфраструктурой).
    
3. Разработка Ansible Playbook для настройки тестового сервера (установка Apache/PHP).
    
4. Создание Jenkins Pipelines для сборки, тестирования, настройки инфраструктуры и деплоя PHP-приложения.
    

---

## 2. Настройка Сервисов и Агентов

### 2.1. Конфигурация Jenkins Controller (Review)

Jenkins Controller запущен в контейнере (`jenkins-controller`) на порту **8080**.

- **Образ:** `jenkins/jenkins:lts`.
    
- **Порты:** 8080 (UI), 50000 (Агенты).
    
- **Установленные Плагины:** Docker, Docker Pipeline, GitHub Integration, **SSH Agent**.
    

### 2.2. Настройка SSH Agent (PHP Build Agent) (Review)

SSH Agent (`ssh-agent`) используется Jenkins для выполнения задач, требующих установки зависимостей Composer и запуска PHPUnit.

- **Dockerfile:** `Dockerfile.ssh_agent`
    
    - **База:** `ubuntu:22.04`
        
    - **Установлено:** `openssh-server`, `openjdk-17-jdk`, `git`, `php-cli`, `composer`.
        
    - **Подключение:** Использует публичный ключ `jenkins_agent.pub` для авторизации Jenkins по SSH под пользователем `jenkins`.
        

### 2.3. Создание и Конфигурация Ansible Agent

Ansible Agent (`ansible-agent`) используется для выполнения Ansible Playbooks.

- **Dockerfile:** `Dockerfile.ansible_agent`
    
    - **База:** `ubuntu:22.04`
        
    - **Установлено:** `ansible` и необходимые SSH-инструменты.
        
    - **Подключение Jenkins:** Использует публичный ключ `jenkins_agent.pub` для авторизации Jenkins по SSH под пользователем `jenkins`.
        
    - **Подключение к Test Server:** В образ скопирован **приватный ключ** `ansible_key`. Этот ключ используется Ansible для подключения к целевому серверу (`test-server`) под пользователем `ansible`.
        

### 2.4. Создание Тестового Сервера

Тестовый сервер (`test-server`) является целевой машиной, управляемой Ansible.

- **Dockerfile:** `Dockerfile.test_server`
    
    - **База:** `ubuntu:22.04`
        
    - **Установлено:** `openssh-server`, `python3` (для работы Ansible).
        
    - **Пользователь:** Создан пользователь `ansible` с правами `sudo NOPASSWD` для удобства Ansible.
        
    - **Подключение:** Публичный ключ `ansible_key.pub` добавлен в `authorized_keys` пользователя `ansible`.
        

---

## 3. Ansible Playbook и Инвентарь

### 3.1. Инвентарь (`ansible/hosts.ini`)

В инвентаре используется имя контейнера (`test-server`) как hostname, так как все контейнеры находятся в одной Docker сети.

Ini, TOML

```
[webservers]
test-server ansible_host=test-server ansible_user=ansible
```

### 3.2. Ansible Playbook (`ansible/setup_test_server.yml`)

Плейбук выполняет начальную настройку тестового сервера.

|**Задача (Task)**|**Модуль**|**Описание**|
|---|---|---|
|Update apt cache|`apt`|Обновление локального кэша пакетов.|
|Install Apache2 and PHP|`apt`|Установка `apache2`, `php`, `libapache2-mod-php`.|
|Ensure Apache is running|`service`|Проверка, что сервис Apache2 запущен и включен в автозагрузку.|

---

## 4. Jenkins Pipelines

Все пайплайны используют **Declarative Pipeline Syntax** и определены в Groovy-скриптах.

### 4.1. Pipeline для Сборки и Тестирования PHP Проекта (`php_build_and_test_pipeline.groovy`) (Review)

- **Агент:** `ssh-agent`.
    
- **Этапы:**
    
    1. **Cloning:** Клонирование репозитория с PHP-проектом.
        
    2. **Install Dependencies:** Выполнение `composer install`.
        
    3. **Run Tests:** Запуск `phpunit` (тестирование PHP-приложения).
        

### 4.2. Pipeline для Конфигурации Сервера (`ansible_setup_pipeline.groovy`)

- **Агент:** `ansible-agent`.
    
- **Этапы:**
    
    1. **Clone Config Repo:** Клонирование репозитория `lab05` для доступа к Ansible Playbook.
        
    2. **Setup Server:** Запуск `ansible-playbook -i hosts.ini setup_test_server.yml`. Этот этап конфигурирует ОС на целевом сервере (устанавливает веб-сервер и PHP).
        

### 4.3. Pipeline для Деплоя PHP Проекта (`php_deploy_pipeline.groovy`)

- **Агент:** `ansible-agent`.
    
- **Этапы:**
    
    1. **Clone Config Repo:** Клонирование репозитория `lab05`.
        
    2. **Deploy App:** Запуск `ansible-playbook -i hosts.ini deploy_app.yml`. Этот плейбук использует модуль `copy` (или `git`) для размещения кода в `/var/www/html` на `test-server`.
        

---

## 5. Ответы на Вопросы

### 5.1. Каковы преимущества использования Ansible для конфигурации сервера?

- **Agentless (Безагентность):** Это главное преимущество. Ansible не требует установки специального программного обеспечения (агента) на управляемые узлы. Для работы достаточно SSH и Python, которые часто предустановлены или легко доступны.
    
- **Idempotency (Идемпотентность):** Плейбуки могут быть запущены многократно без изменения состояния системы, если она уже соответствует описанной конфигурации. Это предотвращает ненужные перезапуски и ошибки.
    
- **YAML (Простота):** Ansible использует синтаксис YAML, который легко читать и писать, даже для не-программистов, что снижает порог вхождения.
    

### 5.2. Какие другие Ansible модули существуют для конфигурационного управления?

Ansible имеет обширную коллекцию модулей. Помимо использованных (`apt`, `service`, `copy`), популярны следующие:

- **`user` / `group`:** Для создания, изменения или удаления системных пользователей и групп.
    
- **`file`:** Для управления файлами, директориями и симлинками (установка прав, создание, удаление).
    
- **`template`:** Использует Jinja2 для создания файлов конфигурации на основе переменных и шаблонов (идеально для `httpd.conf` или `nginx.conf`).
    
- **`systemd`:** Расширенное управление службами (более современный аналог `service`).
    
- **`lineinfile` / `blockinfile`:** Для модификации содержимого файлов, например, для добавления одной строки в конец файла или целого блока конфигурации.
    

### 5.3. Какие проблемы вы обнаружили при создании Ansible Playbook и как их решили?

| **Проблема**                      | **Причина**                                                                                              | **Решение**                                                                                                                             |
| --------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **"No Python Interpreter found"** | Ansible требует наличия Python на управляемом узле (даже для Ubuntu).                                    | В `Dockerfile.test_server` был явно установлен `python3`.                                                                               |
| **"Permission denied" / `sudo`**  | Ansible подключался под пользователем `ansible`, но для установки пакетов требовались права `root`.      | В плейбуке использован параметр `become: yes`, а в `Dockerfile.test_server` настроен `NOPASSWD` для пользователя `ansible` в `sudoers`. |
| **"Host key checking failed"**    | Впервые подключаясь к новому контейнеру, SSH-клиент Ansible-агента запрашивал подтверждение ключа хоста. | В `Dockerfile.ansible_agent` был добавлен параметр `StrictHostKeyChecking no` в `/etc/ssh/ssh_config`, чтобы автоматизировать процесс.  |
