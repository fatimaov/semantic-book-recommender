from enum import Enum


class BookCategory(str, Enum):
    FICTION = "Fiction"
    NONFICTION = "Nonfiction"
    CHILDRENS_FICTION = "Children's Fiction"
    CHILDRENS_NONFICTION = "Children's Nonfiction"
