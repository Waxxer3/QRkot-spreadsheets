from typing import Optional, Tuple

import httpx
from fastapi import HTTPException, status

YANDEX_DISK_BASE_URL = 'https://cloud-api.yandex.net/v1/disk'
REPORTS_FOLDER = 'QRKot Reports'

EXCEL_CONTENT_TYPE = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)


class YandexDiskClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = YANDEX_DISK_BASE_URL
        self.headers = {'Authorization': f'OAuth {token}'}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def create_excel_file(
        self, filename: str, folder: str = REPORTS_FOLDER
    ) -> Tuple[str, str]:
        await self._create_folder(folder)

        file_path = f'disk:/{folder}/{filename}.xlsx'

        response = await self._client.get(
            f'{self.base_url}/resources/upload',
            headers=self.headers,
            params={'path': file_path, 'overwrite': 'true'},
        )
        response.raise_for_status()

        upload_url = response.json().get('href')
        if not upload_url:
            raise ValueError(
                'Яндекс Диск не вернул ссылку для загрузки файла'
            )

        return upload_url, file_path

    async def upload_file(self, upload_url: str, content: bytes) -> None:
        response = await self._client.put(
            upload_url,
            content=content,
            headers={'Content-Type': EXCEL_CONTENT_TYPE},
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        response = await self._client.put(
            f'{self.base_url}/resources/publish',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()

        response = await self._client.get(
            f'{self.base_url}/resources',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()

        public_url = response.json().get('public_url')
        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    'Яндекс Диск не вернул публичную ссылку на файл'
                ),
            )
        return public_url

    async def _create_folder(self, folder: str) -> None:
        response = await self._client.put(
            f'{self.base_url}/resources',
            headers=self.headers,
            params={'path': f'disk:/{folder}'},
        )
        if response.status_code == httpx.codes.CONFLICT:
            return
        response.raise_for_status()


async def get_yandex_client():
    from app.core.config import settings

    if not settings.yandex_disk_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                'Яндекс Диск не настроен. Добавьте YANDEX_DISK_TOKEN '
                'в .env-файл'
            ),
        )

    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
