import os

# from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f = open('books.csv', 'r')
f.readline()
count = 0

for line in f:   
    line = line.strip().split(",")

    isbn = line[0]
    year = int(line[-1])

    if len(line) == 5:
        if "\"" in line[1]:
            title = line[1].strip("\"")+","+line[2].strip("\"")
            author = line[-2]
        else:
            title = line[1]
            author = line[2].strip("\"")+","+line[3].strip("\"")
    else:
        title = line[1]
        author = line[-2]

    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn":isbn, "title":title, "author":author, "year":year})
    db.commit()

    # print(isbn,title,author,year)