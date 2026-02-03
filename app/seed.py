from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Building, Organization, Phone


async def seed(session: AsyncSession) -> None:
    """Заполняет БД тестовыми данными. Идемпотентна - пропускает если данные есть."""
    from sqlalchemy import select

    result = await session.execute(select(Building))
    if result.scalars().first():
        return


    b1 = Building(address="г. Москва, ул. Ленина 1, офис 3", latitude=55.7558, longitude=37.6173)
    b2 = Building(address="г. Москва, Блюхера 32/1", latitude=55.7900, longitude=37.5600)
    b3 = Building(address="г. Санкт-Петербург, Невский пр. 10", latitude=59.9350, longitude=30.3200)
    session.add_all([b1, b2, b3])
    await session.flush()


    food = Activity(name="Еда", parent_id=None, depth=1)
    cars = Activity(name="Автомобили", parent_id=None, depth=1)
    session.add_all([food, cars])
    await session.flush()


    meat = Activity(name="Мясная продукция", parent_id=food.id, depth=2)
    dairy = Activity(name="Молочная продукция", parent_id=food.id, depth=2)
    trucks = Activity(name="Грузовые", parent_id=cars.id, depth=2)
    passenger = Activity(name="Легковые", parent_id=cars.id, depth=2)
    session.add_all([meat, dairy, trucks, passenger])
    await session.flush()


    parts = Activity(name="Запчасти", parent_id=passenger.id, depth=3)
    accessories = Activity(name="Аксессуары", parent_id=passenger.id, depth=3)
    session.add_all([parts, accessories])
    await session.flush()


    org1 = Organization(name='ООО "Рога и Копыта"', building_id=b1.id)
    org1.phones = [Phone(number="2-222-222"), Phone(number="3-333-333")]
    org1.activities = [meat, dairy]

    org2 = Organization(name='ЗАО "Молоко+"', building_id=b1.id)
    org2.phones = [Phone(number="8-923-666-13-13")]
    org2.activities = [dairy]

    org3 = Organization(name='ОАО "Грузоперевозки"', building_id=b2.id)
    org3.phones = [Phone(number="8-800-123-45-67")]
    org3.activities = [trucks]

    org4 = Organization(name='МП "Автозапчасти Nord"', building_id=b3.id)
    org4.phones = [Phone(number="812-111-22-33"), Phone(number="812-444-55-66")]
    org4.activities = [parts, accessories]

    org5 = Organization(name="ИП Петров - Легковые", building_id=b2.id)
    org5.phones = [Phone(number="499-000-11-22")]
    org5.activities = [passenger]

    session.add_all([org1, org2, org3, org4, org5])
    await session.commit()
