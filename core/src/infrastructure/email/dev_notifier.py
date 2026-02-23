from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


class DevLogNotifier:
    def send_password_reset(self, email: str, token: str) -> None:
        logger.info("password_reset_requested email=%s token=%s", email, token)
