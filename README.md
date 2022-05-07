# Proxybus

## Первый запуск

* Создаем виртуальное окружение
    ```shell
    python3 -m venv venv
    ```
  
* Активируем виртуальное окружение
    ```shell
    $ source venv/bin/activate # unix
    
    workingdir:\> venv\Scripts\activate.bat # cmd.exe
    
    PS workingdir:\> venv\Scripts\Activate.ps1 # PowerShell
    ```
  
* Устанавливаем зависимости
  * Если есть poetry
    ```shell
    poetry install
    ```
  * Используя pip
    ```shell
    pip install -r requirements.txt
    ```
  
* Настраиваем

  * Заполняем конфигурацию в config.py
  

* Запускаем
  ```shell
  python3 main.py
  ```
