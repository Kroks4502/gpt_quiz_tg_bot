# Quiz GPT Bot

Quiz GPT Bot is a Telegram bot designed to create engaging quizzes based on user-provided topics. It leverages OpenAI's GPT models to generate unique quiz questions and subtopics, providing an interactive learning experience.

> [!TIP]
> [Try it now on Telegram @qz_chat_bot](https://t.me/qz_chat_bot)

## Features

- **Quiz Generation**: Automatically generates quiz questions based on user-specified topics.
- **Subtopic Exploration**: Breaks down main topics into subtopics for more detailed quizzes.
- **User Interaction**: Supports various commands and interactions through Telegram.
- **Database Integration**: Utilizes PostgreSQL for storing user data and quiz history.
- **Asynchronous Operations**: Built with asynchronous programming for efficient performance.

## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Telegram Bot API credentials
- OpenAI API key

### Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/Kroks4502/gpt_quiz_tg_bot.git
    cd gpt_quiz_tg_bot
    ```

2. **Configure Environment Variables**

    Create a [.env](.env.example) file in the root directory with the following content:

    ```env
    TELEGRAM__API_ID=your_telegram_api_id
    TELEGRAM__API_HASH=your_telegram_api_hash
    TELEGRAM__BOT_TOKEN=your_telegram_bot_token
    OPENAI__API_KEY=your_openai_api_key
    DATABASE__DSN=postgresql+asyncpg://user:password@localhost/dbname
    
    # for docker
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
    POSTGRES_DB: dbname
    ```

3. **Start the Docker Container**

    ```shell
    docker compose up -d
    ```

4. **Run Database Migrations**

    Ensure your database is set up and run migrations using Alembic:

    ```shell
    docker compose exec backend alembic upgrade head
    ```

## Usage

Interact with the Bot

* Use /start to begin interaction.
* Send a topic to generate a quiz.
* Use /menu to access different settings and options.
* Use /stop to halt any ongoing quiz sessions.

## Development

### Code Structure

* **/src**
  * **/bot**: Contains the bot logic and handlers.
  * **/db**: Database models and session management.
  * **/gpt**: GPT integration for question and subtopic generation.
  * **/config.py**: Configuration management using Pydantic.
  * **/log.py**: Logging configuration.

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Commands

Create migration file:

```sh
scripts/autogenerate_migrations.sh "auto"
```

Run migration:

```sh
scripts/run_migrations.sh
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
