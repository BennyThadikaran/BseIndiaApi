FROM python:3.8.18-slim-bullseye

WORKDIR /app

RUN pip install -U requests mthrottle

RUN echo 'from bse import BSE\n\
with BSE("./") as bse:\n\t\
print(bse.getScripCode("hdfcbank"))\n\
print("all working well")' > test.py

COPY bse/ bse/
COPY __init__.py .

CMD ["python3", "test.py"]
