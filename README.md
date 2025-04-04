#### Technologies:
 - Python == 3.10
 - MongoDB == 7.0.14

#### Environment variables:
    Required:
        ADMIN_ID - Telegram id to send admin notifications
        BOT_TOKEN - Telegram bot token
        MONGO_URL - MongoDB connection string
        MONGO_DB_NAME - MongoDB Database name
        LLM_MODEL - LLM model to generate event conception
        OPEN_AI_TOKEN - Open ai api token
        BASE_AI_URL - AI url
        MAX_SURVEYS_NUMBER - max surveys that user can take

    Other:
        MAX_RETRIES - number of conception generate retries
        RETRY_DELAY_MINUTES - delay between generation tries