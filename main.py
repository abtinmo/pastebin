from sanic import Sanic
from sanic.response import html, redirect
import uuid
import aiofiles
import psycopg2
import asyncpg
from config import DATABASE, DB_PASSWORD, DB_USER

app = Sanic()


@app.route("/", methods=["GET"])
async def get(request):
    async with aiofiles.open('templates/index.html', mode='r') as f:
        template = await f.read()
    return html(template)


@app.route("/", methods=["POST"])
async def get(request):
    data = request.form["message"][0]
    insert_sql = "INSERT INTO tb_pastes(id, content) VALUES($1, $2);"
    # conn = psycopg2.connect(host="localhost", database=DATABASE,
    #  user=DB_USER,
    #                        password=DB_PASSWORD)
    paste_id = uuid.uuid4().hex
    params = [paste_id, data]
    # cur = conn.cursor()
    # cur.execute(insert_sql, params)
    # conn.commit()
    # conn.close()
    con = await asyncpg.connect(host="localhost", database=DATABASE,
                                user=DB_USER, password=DB_PASSWORD)
    await con.execute(insert_sql, paste_id, data)
    await con.close()
    url = app.url_for('paste', paste_id=paste_id)
    return redirect(url)


@app.route("/<paste_id:[A-z0-9]{32}>", methods=["GET"])
async def paste(request, paste_id):
    insert_sql = "SELECT content  FROM tb_pastes WHERE id = $1;"
    con = await asyncpg.connect(host="localhost", database=DATABASE,
                                user=DB_USER, password=DB_PASSWORD)
    data = await con.fetchrow(insert_sql, paste_id)
    await con.close()
    async with aiofiles.open('templates/index1.html', 'r') as f:
        template = await f.read()
    template = str(template)
    length = data[0].count("\r")
    template = template.replace("#LENGTH#", str(length))
    template = template.replace("#CONTENT#", data[0])
    return html(template)


if __name__ == '__main__':
    app.run(port=8000, host="0.0.0.0")
