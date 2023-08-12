from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    email = models.EmailField(
        "Адрес электронной почты",
        unique=True,
        error_messages={
            "unique": "Пользователь с такой почтой уже существует."
        },
    )
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    """Модель для подписок."""

    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="following",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")), name="check_follow"
            ),
        )

    def __str__(self) -> str:
        return f"{self.user.username} follows {self.author.username}"
