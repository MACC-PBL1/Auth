from sqlalchemy.future import select
from app.sql.models import Role, User

async def init_admin(db):
    """Crea roles base y usuario admin si no existen."""

    # --- Crear roles base ---
    base_roles = ["admin", "client", "manager"]

    for role_name in base_roles:
        result = await db.execute(select(Role).where(Role.name == role_name))
        role = result.scalars().first()
        if not role:
            role = Role(name=role_name, description=f"Rol {role_name}")
            db.add(role)
            await db.commit()
            await db.refresh(role)

    # --- Obtener rol admin ---
    result = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalars().first()

    # --- Crear usuario admin si no existe ---
    result = await db.execute(select(User).where(User.email == "admin@example.com"))
    admin_user = result.scalars().first()
    if not admin_user:
        admin_user = User(
            name="Administrador",
            email="admin@example.com",
            is_active=True,
            role_id=admin_role.id,
        )
        admin_user.set_password("Admin1234")
        db.add(admin_user)
        await db.commit()
        print("Usuario admin creado con éxito.")