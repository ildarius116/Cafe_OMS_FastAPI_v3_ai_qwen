"""Сервис для управления пользователями."""

from typing import Optional, List

from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from app.models.user import User, UserLevel, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, PermissionError


class UserService:
    """
    Сервис для операций с пользователями.
    
    Инкапсулирует бизнес-логику и работу с базой данных.
    """
    
    def __init__(self, db: Session):
        """
        Инициализирует сервис.
        
        Args:
            db: Сессия базы данных.
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> User:
        """
        Получает пользователя по ID.
        
        Args:
            user_id: Уникальный идентификатор пользователя.
        
        Returns:
            Объект пользователя.
        
        Raises:
            NotFoundError: Если пользователь не найден.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Получает пользователя по email.
        
        Args:
            email: Электронная почта.
        
        Returns:
            Объект пользователя или None.
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_nickname(self, nickname: str) -> Optional[User]:
        """
        Получает пользователя по никнейму.
        
        Args:
            nickname: Никнейм пользователя.
        
        Returns:
            Объект пользователя или None.
        """
        return self.db.query(User).filter(User.nickname == nickname).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        level: Optional[UserLevel] = None,
        status: Optional[UserStatus] = None
    ) -> List[User]:
        """
        Получает список пользователей с фильтрацией и пагинацией.

        Args:
            skip: Количество пропускаемых записей.
            limit: Максимальное количество записей.
            search: Поисковый запрос (по имени, фамилии, email).
            level: Фильтр по уровню доступа.
            status: Фильтр по статусу.

        Returns:
            Список пользователей.
        """
        query = self.db.query(User)

        # Фильтр по уровню
        if level:
            query = query.filter(User.level == level)

        # Фильтр по статусу
        if status:
            query = query.filter(User.status == status)

        # Получаем результаты
        users = query.offset(skip).limit(limit).all()

        # Поисковый фильтр в Python (для поддержки кириллицы и Unicode)
        if search:
            search_lower = search.lower()
            users = [
                u for u in users
                if search_lower in u.name.lower()
                or search_lower in u.surname.lower()
                or search_lower in u.email.lower()
                or search_lower in u.nickname.lower()
            ]

        return users
    
    def create(self, data: UserCreate, creator_level: UserLevel = UserLevel.ADMIN) -> User:
        """
        Создаёт нового пользователя.

        Args:
            data: Данные для создания пользователя.
            creator_level: Уровень прав создателя (для валидации).

        Returns:
            Созданный объект пользователя.

        Raises:
            ConflictError: Если email или nickname уже заняты.
            PermissionError: Если недостаточно прав для создания с указанным уровнем.
        """
        # Проверка на дубликаты
        if self.get_by_email(data.email):
            raise ConflictError(f"Email '{data.email}' уже занят")
        if self.get_by_nickname(data.nickname):
            raise ConflictError(f"Никнейм '{data.nickname}' уже занят")

        # При регистрации пользователь получает уровень CLIENT
        # Проверка прав только если создаётся пользователь с другим уровнем
        # (это возможно только через админ-панель, не через публичную регистрацию)
        
        # Создание пользователя
        db_user = User(
            nickname=data.nickname,
            name=data.name,
            surname=data.surname,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            level=UserLevel.CLIENT,  # Всегда CLIENT для публичной регистрации
            status=UserStatus.ACTIVE
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update(
        self,
        user_id: int,
        data: UserUpdate,
        updater_level: UserLevel
    ) -> User:
        """
        Обновляет данные пользователя.
        
        Args:
            user_id: ID пользователя для обновления.
            data: Новые данные.
            updater_level: Уровень прав обновляющего.
        
        Returns:
            Обновлённый объект пользователя.
        
        Raises:
            NotFoundError: Если пользователь не найден.
            ConflictError: Если новый email или nickname уже заняты.
            PermissionError: Если недостаточно прав.
        """
        user = self.get_by_id(user_id)
        
        # Проверка прав: нельзя редактировать пользователя с уровнем выше или равным своему
        if user.level in self._get_higher_or_equal_levels(updater_level):
            raise PermissionError("Недостаточно прав для редактирования этого пользователя")
        
        # Проверка прав на изменение уровня
        if data.level and data.level not in self._get_allowed_levels(updater_level):
            raise PermissionError("Нельзя установить такой уровень прав")
        
        # Проверка на дубликаты при смене email/nickname
        if data.email and data.email != user.email:
            if self.get_by_email(data.email):
                raise ConflictError(f"Email '{data.email}' уже занят")
        if data.nickname and data.nickname != user.nickname:
            if self.get_by_nickname(data.nickname):
                raise ConflictError(f"Никнейм '{data.nickname}' уже занят")
        
        # Обновление полей
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int, deleter_level: UserLevel) -> None:
        """
        Удаляет пользователя.
        
        Args:
            user_id: ID пользователя для удаления.
            deleter_level: Уровень прав удаляющего.
        
        Raises:
            NotFoundError: Если пользователь не найден.
            PermissionError: Если недостаточно прав.
        """
        user = self.get_by_id(user_id)
        
        # Проверка прав: нельзя удалять пользователя с уровнем выше или равным своему
        if user.level in self._get_higher_or_equal_levels(deleter_level):
            raise PermissionError("Недостаточно прав для удаления этого пользователя")
        
        self.db.delete(user)
        self.db.commit()
    
    def verify_password(self, user: User, password: str) -> bool:
        """
        Проверяет пароль пользователя.
        
        Args:
            user: Объект пользователя.
            password: Пароль для проверки.
        
        Returns:
            True если пароль верный, False иначе.
        """
        return verify_password(password, user.hashed_password)
    
    def _get_allowed_levels(self, user_level: UserLevel) -> List[UserLevel]:
        """
        Возвращает список уровней, которые может создавать/редактировать пользователь.
        
        Args:
            user_level: Уровень пользователя.
        
        Returns:
            Список доступных уровней.
        """
        hierarchy = [
            UserLevel.GUEST,
            UserLevel.CLIENT,
            UserLevel.STAFF,
            UserLevel.MANAGER,
            UserLevel.ADMIN,
            UserLevel.DIRECTOR,
            UserLevel.SUPERUSER
        ]
        
        try:
            user_index = hierarchy.index(user_level)
        except ValueError:
            return [UserLevel.CLIENT]
        
        # Можно управлять только уровнями ниже своего
        return hierarchy[:user_index]
    
    def _get_higher_or_equal_levels(self, user_level: UserLevel) -> List[UserLevel]:
        """
        Возвращает список уровней, которые выше или равны данному.
        
        Args:
            user_level: Уровень пользователя.
        
        Returns:
            Список уровней выше или равных.
        """
        hierarchy = [
            UserLevel.GUEST,
            UserLevel.CLIENT,
            UserLevel.STAFF,
            UserLevel.MANAGER,
            UserLevel.ADMIN,
            UserLevel.DIRECTOR,
            UserLevel.SUPERUSER
        ]
        
        try:
            user_index = hierarchy.index(user_level)
        except ValueError:
            return hierarchy
        
        return hierarchy[user_index:]
