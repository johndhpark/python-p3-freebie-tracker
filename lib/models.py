from sqlalchemy import ForeignKey, Column, Integer, Float, String, MetaData, Table, create_engine
from sqlalchemy.event import attr
from sqlalchemy.orm import relation, relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

engine = create_engine('sqlite:///freebies.db')
Session = sessionmaker(bind=engine)
session = Session()

company_dev = Table(
    "companies_devs",
    Base.metadata,
    Column("company_id", ForeignKey("companies.id"), primary_key=True),
    Column("dev_id", ForeignKey("devs.id"), primary_key=True),
    extend_existing=True,
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    founding_year = Column(Integer)

    freebies = relationship("Freebie", backref=backref("company"))
    devs = relation("Dev", secondary=company_dev, back_populates="companies")

    def __init__(self, name, founding_year):
        self.name = name
        self.founding_year = founding_year

    def __repr__(self):
        return f"<Company name: {self.name}, founded: {self.founding_year}>"

    def give_freebie(self, dev, item_name, value):
        freebie = Freebie(item_name=item_name, value=value, company_id=self.id, dev_id=dev.id)

        session.add(freebie)
        session.commit()

        return freebie

    @classmethod
    def oldest_company(cls):
        return session.query(cls).order_by(cls.founding_year).first()


class Dev(Base):
    __tablename__ = "devs"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    freebies = relationship("Freebie", backref=backref("dev"))
    companies = relationship("Company", secondary=company_dev, back_populates="devs")

    def __repr__(self):
        return f"<Dev {self.name}>"

    def received_one(self, item_name):
        matching_freebies = session.query(Freebie).filter(Freebie.item_name == item_name, Freebie.dev_id == self.id).all()
        return len(matching_freebies) > 0

    def give_away(self, dev, freebie):
        print("Before: freebie dev id is ", freebie.dev_id)

        if freebie.dev_id == self.id:
            freebie.dev_id = dev.id

        session.commit()

        print("After freebie dev id is ", freebie.dev_id)

class Freebie(Base):
    __tablename__ = "freebies"

    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    value = Column(Float())

    company_id = Column(Integer(), ForeignKey("companies.id"))
    dev_id = Column(Integer(), ForeignKey("devs.id"))

    def __repr__(self):
        return f"<Freebie name: {self.item_name}, value: ${self.value}>"

    def print_details(self):
        dev = self.dev
        company = self.company

        return f"{dev.name} owns a {self.item_name} from {company.name}."
