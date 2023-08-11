#!/usr/bin/env python3

# Script goes here!
import random

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Company, Dev, Freebie

if __name__ == "__main__":
    print("🌱 Seeding DB...")
    engine = create_engine("sqlite:///freebies.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Company).delete()
    session.query(Dev).delete()
    session.query(Freebie).delete()

    faker = Faker()

    # Create bunch of companies
    companies = []

    for _ in range(10):
        company = Company(name=faker.company(), founding_year=faker.year())
        session.add(company)
        session.commit()
        companies.append(company)

    # Create bunch of devs
    devs = []

    for _ in range(10):
        dev = Dev(name=faker.name())
        session.add(dev)
        session.commit()
        devs.append(dev)

    # Create bunch of freebies
    items = [
        ("pen", 1.00),
        ("shirt", 10.50),
        ("stickers", 2.10),
        ("mug", 15.00),
        ("backpack", 55.15),
        ("notebook", 7.15),
        ("mousepad", 12.20)
    ]

    freebies = []   

    for company in companies:
        for i in range(random.randint(0, 5)):
            dev = random.choice(devs)

            if company not in dev.companies:
                dev.companies.append(company)
                session.add(dev)

            item = items[i]
            freebie = Freebie(
                item_name=item[0], value=item[1], company_id=company.id, dev_id=dev.id
            )

            freebies.append(freebie)

    session.bulk_save_objects(freebies)
    session.commit()
    session.close()

    print("✅ Done seeding!")
