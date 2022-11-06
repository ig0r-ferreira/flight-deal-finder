import pydantic


class SheetAPISettings(pydantic.BaseSettings):
    SPREADSHEET_URL: pydantic.HttpUrl

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
