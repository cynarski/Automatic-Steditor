# Tutaj bedzie nasz skrypcik pythonowy do przebiegu programu
import app
import dbconnector


def main():
    #fixme to bedzie usuniete i wykonywanie tylko w solve_engine
    con = dbconnector.conncect_to_db()
    trucks = dbconnector.dbGetQuery(con, "SELECT * FROM trucks")
    products = dbconnector.dbGetQuery(con, "SELECT * FROM products")
    dbconnector.close_connection(con)

    print(trucks)
    print(products)


# if __name__ == "__main__":
main()
app.run_all()

