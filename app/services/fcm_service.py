from firebase_admin import messaging

from app.utils.logger import logger

import asyncio
from typing import Optional
from typing import List
from typing import Dict
from typing import Optional


class FcmService:

    def __init__(self):
        pass

    def _sanitize_data(
        self,
        data: Optional[dict],
    ) -> Dict[str, str]:

        if not data:
            return {}

        result = {}

        for key, value in data.items():

            result[str(key)] = str(value)

        return result

    def _build_android_config(
        self,
        priority: str,
        ttl: Optional[int],
        collapse_key: Optional[str],
    ):

        return messaging.AndroidConfig(

            priority=priority,

            ttl=ttl,

            collapse_key=collapse_key,
            notification=messaging.AndroidNotification(
                channel_id="default_channel",
                sound="default",
            )
        )

    def _build_apns_config(self):

        return messaging.APNSConfig(

            headers={

                "apns-priority": "10",

            },
        )

    def _build_notification(
        self,
        title: str,
        body: str,
    ):

        return messaging.Notification(

            title=title,

            body=body,
        )

    def _log_success(
        self,
        target,
        response,
    ):

        logger.info(

            "FCM success target=%s response=%s",

            target,

            response,
        )

    def _log_error(
        self,
        target,
    ):

        logger.exception(

            "FCM failed target=%s",

            target,
        )

    async def send_to_token(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "high",
        ttl: Optional[int] = None,
        collapse_key: Optional[str] = None,
        retries: int = 3,
        dry_run: bool = False,
    ):

        for attempt in range(retries):

            try:

                android_config = self._build_android_config(

                    priority,

                    ttl,

                    collapse_key,
                )

                apns_config = self._build_apns_config()

                message = messaging.Message(

                    token=token,

                    notification=self._build_notification(

                        title,

                        body,
                    ),

                    android=android_config,

                    apns=apns_config,

                    data=self._sanitize_data(

                        data,
                    ),
                )

                response = messaging.send(

                    message,

                    dry_run=dry_run,
                )

                self._log_success(

                    token,

                    response,
                )

                return response

            except Exception:

                self._log_error(

                    token,
                )

                if attempt < retries - 1:

                    await asyncio.sleep(

                        2 ** attempt,
                    )

        return None

    async def send_to_tokens(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "high",
        ttl: Optional[int] = None,
        collapse_key: Optional[str] = None,
        dry_run: bool = False,
    ):

        try:

            tokens = [

                token

                for token in tokens

                if token

            ]

            if not tokens:

                return None

            # BƯỚC 1: Gộp title và body vào chung gói data
            payload_data = {
                "title": title,
                "body": body,
            }
            if data:
                payload_data.update(data)

            android_config = self._build_android_config(priority, ttl, collapse_key)
            apns_config = self._build_apns_config()

            message = messaging.MulticastMessage(
                tokens=tokens,
                # BƯỚC 2: Tắt dòng notification này đi (RẤT QUAN TRỌNG)
                # notification=self._build_notification(title, body),
                
                android=android_config,
                apns=apns_config,
                
                # BƯỚC 3: Truyền gói data đã gộp vào
                data=self._sanitize_data(payload_data),
            )

            response = messaging.send_each_for_multicast(

                message,

                dry_run=dry_run,
            )

            self._log_success(

                f"multicast:{len(tokens)} tokens",

                (
                    f"success={response.success_count}, "

                    f"failed={response.failure_count}"
                ),
            )

            return response

        except Exception:

            self._log_error(

                f"multicast:{len(tokens)} tokens",
            )

            return None

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "high",
        ttl: Optional[int] = None,
        collapse_key: Optional[str] = None,
        dry_run: bool = False,
    ):

        try:

            # BƯỚC 1: Gộp title và body vào chung gói data
            payload_data = {
                "title": title,
                "body": body,
            }
            if data:
                payload_data.update(data)

            android_config = self._build_android_config(priority, ttl, collapse_key)
            apns_config = self._build_apns_config()

            message = messaging.Message(
                topic=topic,
                # BƯỚC 2: Tắt dòng notification
                # notification=self._build_notification(title, body),
                
                android=android_config,
                apns=apns_config,
                
                # BƯỚC 3: Truyền gói data
                data=self._sanitize_data(payload_data),
            )

            response = messaging.send(

                message,

                dry_run=dry_run,
            )

            self._log_success(

                f"topic:{topic}",

                response,
            )

            return response

        except Exception:

            self._log_error(

                f"topic:{topic}",
            )

            return None