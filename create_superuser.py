"""Скрипт для создания суперпользователя."""

from app.database import SessionLocal
from app.models.user import User, UserLevel, UserStatus
from app.core.security import get_password_hash


def create_superuser():
    """Создаёт суперпользователя."""
    
    db = SessionLocal()
    
    try:
        # Проверка на существование
        existing_user = db.query(User).filter(
            (User.email == "super_good@cafe.ru") | 
            (User.nickname == "super_good")
        ).first()
        
        if existing_user:
            print("⚠️ Пользователь уже существует!")
            return
        
        # Создание суперпользователя
        superuser = User(
            nickname='super_good',
            name='Вася',
            surname='Пупкин',
            email='super_good@cafe.ru',
            level=UserLevel.SUPERUSER,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash('12345')
        )
        
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print("✅ Суперпользователь успешно создан!")
        print(f"\nДанные для входа:")
        print(f"  Email: {superuser.email}")
        print(f"  Пароль: 12345")
        print(f"  Уровень: {superuser.level.value}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_superuser()
