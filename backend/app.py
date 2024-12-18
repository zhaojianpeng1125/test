# import caching as caching
from flask import Flask, jsonify, request
from sqlalchemy import text

from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
import auth
# from aliyunsms.sms_send import send_sms
import json
import random
import datetime
from redis import StrictRedis

# 创建redis对象
redis_store = StrictRedis(host=BaseConfig.REDIS_HOST, port=BaseConfig.REDIS_PORT, decode_responses=True)

# 跨域
from flask_cors import CORS
from flask_cors import cross_origin

app = Flask(__name__)

# 添加配置数据库
app.config.from_object(BaseConfig)
# 初始化拓展,app到数据库的ORM映射
db = SQLAlchemy(app)

# 检查数据库连接是否成功
with app.app_context():
    with db.engine.connect() as conn:
        rs = conn.execute(text("select 1"))
        print(rs.fetchone())

# 用户登录
@app.route("/api/user/login", methods=["POST"])
@cross_origin()
def user_login():
    print(request.json)
    userortel = request.json.get("userortel").strip()
    password = request.json.get("password").strip()
    sql = ('select * ' \
           + 'from user ' \
           + 'where telephone = "{0}" and password = "{1}"').format(userortel, password)
    data = db.session.execute(text(sql)).first()
    print(data)
    if data != None:
        user = {'id': data[0], 'username': data[1], 'password': data[2], 'telephone': data[3]}
        # 生成token
        token = auth.encode_func(user)
        print(token)
        return jsonify({"code": 200, "msg": "登录成功", "token": token, "role": data[4]})
    else:
        return jsonify({"code": 1000, "msg": "用户名或密码错误"})

# 用户界面获取店铺信息
@app.route("/api/user/shop", methods=["GET"])
@cross_origin()
def user_get_shop():
    data = db.session.execute(text('select * from product')).fetchall()

    Data = []
    for i in range(len(data)):
        dic = dict(shop_name=data[i][0], price=data[i][1], sale=data[i][2])
        Data.append(dic)
    print(Data)
    return jsonify(status=200, tabledata=Data)

# 下订单
@app.route("/api/user/addorder", methods=["POST"])
@cross_origin()
def user_addorder():
    rq = request.json
    # 获取各个参数
    shopname = rq.get("shop_name")
    ordermoney = rq.get("order_money")
    orderway = rq.get("order_way")
    consphone = get_token_phone(request.headers.get('token'))
    consname = rq.get("cons_name")
    consaddre = rq.get("cons_addre")
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.session.execute(text(
        'insert into oorder( shop_name, order_money, order_way, cons_phone, cons_name, cons_addre,create_time) value("%s", %f, "%s", "%s", "%s", "%s","%s")' % (
            shopname, float(ordermoney), orderway, consphone, consname, consaddre, create_time)))
    db.session.commit()
    return jsonify(status=200, msg="成功下单")

def get_token_phone(token):
    data = auth.decode_func(token)
    phone = data['telephone']
    return phone

@app.route("/api/user/unsend", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_unsend():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        data = db.session.execute(text('SELECT * FROM oorder WHERE checked=0 AND cons_phone=:phone'), {'phone': phone}).fetchall()
        Data = [
            {
                'order_id': row[0],
                'shop_name': row[1],
                'price': row[2],
                'orderway': row[3],
                'cons_name': row[5],
                'cons_addre': row[6],
                'create_time': row[8]
            } for row in data
        ]
        return jsonify(status=200, tabledata=Data)

    if request.method == 'POST':
        rq = request.json
        order_id = rq.get("order_id")
        cons_name = rq.get("cons_name")
        cons_addre = rq.get("cons_addre")
        db.session.execute(
            text('UPDATE oorder SET cons_name=:cons_name, cons_addre=:cons_addre WHERE order_id=:order_id'),
            {'cons_name': cons_name, 'cons_addre': cons_addre, 'order_id': order_id}
        )
        db.session.commit()
        return jsonify(status=200, msg="修改成功")

    if request.method == 'DELETE':
        order_id = request.json.get("delete_id")
        db.session.execute(text('DELETE FROM oorder WHERE order_id=:order_id'), {'order_id': order_id})
        db.session.commit()
        return jsonify(status=200, msg="删除成功")


@app.route("/api/user/sending", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_sending():
    if request.培养合method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        data = db.session.execute(text('SELECT * FROM sending_order WHERE cons_phone=:phone'), {'phone': phone}).fetchall()
        Data = [
            {
                'order_id': row[0],
                'shop_name': row[1],
                'order_money': row[2],
                'order_way': row[3],
                'cons_phone': row[4],
                'cons_name': row[5],
                'cons_addre': row[6],
                'disp_id': row[7],
                'deliver_time': row[8],
                'disp_phone': row[9]
            } for row in data
        ]
        return jsonify(status=200, tabledata=Data)

@app.route("/api/user/sended", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_sended():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        data = db.session.execute(text('SELECT * FROM sended_order WHERE cons_phone=:phone'), {'phone': phone}).fetchall()
        Data = [
            {
                'order_id': row[0],
                'shop_name': row[1],
                'order_money': row[2],
                'order_way': row[3],
                'cons_phone': row[4],
                'cons_name': row[5],
                'cons_addre': row[6],
                'disp_id': row[7],
                'deliver_time': row[8],
                'disp_phone': row[9]
            } for row in data
        ]
        return jsonify(status=200, tabledata=Data)

@app.route("/api/user/usermsg", methods=["POST", "GET"])
@cross_origin()
def usermsg():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        data = db.session.execute(text('select * from user_msg where phone="%s"' % phone)).fetchall()
        if not data:
            return jsonify(status=404, msg="未找到用户信息")
        Data = dict(real_name=data[0][1], sex=data[0][2], age=data[0][3], mail=data[0][4], phone=data[0][5], user_name=data[0][6])
        return jsonify(status=200, data=Data)

@app.route("/api/user/pwd_chg", methods=["POST"])
@cross_origin()
def user_pwd_chg():
    if request.method=='POST':
        pwd=request.json.get('new_pwd')
        old_pwd=request.json.get('old_pwd')
        phone = get_token_phone(request.headers.get('token'))
        data = db.session.execute(text('select * from user where telephone="%s" and password="%s"'% (phone,old_pwd))).fetchall()
        if not data:
            return jsonify(status=1000,msg="原始密码错误")
        else:
            db.session.execute(text('update user set password="%s" where telephone="%s"'% (pwd,phone)))
            db.session.commit()
            return jsonify(status=200,msg="修改成功")

@app.route("/api/manager/shop", methods=["POST", "GET", "DELETE"])
@cross_origin()
def manager_shop():
    # 获取店铺信息
    if request.method == 'GET':
        data = db.session.execute(text('select * from product')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(shop_name=data[i][0], price=data[i][1], sale=data[i][2])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)
    if request.method == 'POST' and request.json.get('action') == "add":
        rq = request.json
        shop_name = rq.get('shop_name')
        price = rq.get('price')
        m_sale_v = rq.get('m_sale_v')
        exist = db.session.execute(text('select * from product where shop_name="%s"' % shop_name)).fetchall()
        if not exist:
            db.session.execute(text('insert product(shop_name,price,m_sale_v) value("%s",%d,%d)' % (
                shop_name, int(price), int(m_sale_v))))
            db.session.commit()
            return jsonify(status=200, msg="添加成功")
        else:
            return jsonify(status=1000, msg="该店铺已存在")

    if request.method == 'POST' and request.json.get('action') == "change":
        rq = request.json
        shop_name = rq.get('shop_name')
        price = rq.get('price')
        m_sale_v = rq.get('m_sale_v')
        db.session.execute(text('update product set price="%d", m_sale_v="%d" where shop_name="%s" ' % (
            int(price), int(m_sale_v), shop_name)))
        db.session.commit()
        return jsonify(status=200, msg="修改成功")
    if request.method == 'DELETE':
        want_delete = request.json.get('want_delete')
        db.session.execute(text('delete from product where shop_name="%s"' % want_delete))
        db.session.commit()
        return jsonify(status=200, msg="删除成功")

@app.route("/api/manager/server", methods=["POST", "GET", "DELETE"])
@cross_origin()
def manager_server():
    if request.method == 'GET':
        data = db.session.execute(text('select * from server')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(service_id=data[i][0], service_name=data[i][1], product_name=data[i][2])
            Data.append(dic)
        shop_range = db.session.execute(text('select shop_name from product')).fetchall()
        Shop = []
        for i in range(len(shop_range)):
            dic = dict(shop_name=shop_range[i][0])
            Shop.append(dic)
        print(Shop)
        return jsonify(status=200, tabledata=Data, shop_range=Shop)
    if request.method == 'POST':
        rq = request.json
        service_id = rq.get('service_id')
        service_name = rq.get('service_name')
        product_name = rq.get('product_name')
        exist = db.session.execute(text('select * from server where service_id="%s"' % service_id)).fetchall()
        if not exist:
            db.session.execute(text('insert server(service_id,service_name,product_name) value("%s","%s","%s")' % (
                service_id, service_name, product_name)))
            db.session.commit()
            return jsonify(status=200, msg="添加成功")
        else:
            return jsonify(status=1000, msg="该编号已存在")
    if request.method == 'DELETE':
        want_delete = request.json.get('want_delete')
        db.session.execute(text('delete from server where service_id="%s"' % want_delete))
        db.session.commit()
        return jsonify(status=200, msg="解雇成功")

@app.route("/api/manager/dispatcher", methods=["POST", "GET", "DELETE"])
@cross_origin()
def manager_dispatcher():
    if request.method == 'GET':
        data = db.session.execute(text('select * from dispatcher')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(dispatcher_id=data[i][0], dispatcher_name=data[i][1], dispatcher_phone=data[i][2])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)
    if request.method == 'POST':
        rq = request.json
        dispatcher_id = rq.get('dispatcher_id')
        dispatcher_name = rq.get('dispatcher_name')
        dispatcher_phone = rq.get('dispatcher_phone')
        exist = db.session.execute(text('select * from dispatcher where dispatcher_id="%s"' % dispatcher_id)).fetchall()
        if not exist:
            db.session.execute(
                text('insert dispatcher(dispatcher_id,dispatcher_name,dispatcher_phone) value("%s","%s","%s")' % (
                    dispatcher_id, dispatcher_name, dispatcher_phone)))
            db.session.commit()
            return jsonify(status=200, msg="添加成功")
        else:
            return jsonify(status=1000, msg="该编号已存在")
    if request.method == 'DELETE':
        want_delete = request.json.get('want_delete')
        db.session.execute(text('delete from dispatcher where dispatcher_id="%s"' % want_delete))
        db.session.commit()
        return jsonify(status=200, msg="解雇成功")

@app.route("/api/manager/wuliu", methods=["GET"])
@cross_origin()
def manager_wuliu():
    ended = request.args.get('id')
    if ended == '0':
        data = db.session.execute(text('select * from wuliu where ended=0')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], cons_phone=data[i][1], disp_id=data[i][2], deliver_time=data[i][3])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)
    else:
        data = db.session.execute(text('select * from wuliu where ended=1')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], cons_phone=data[i][1], disp_id=data[i][2], deliver_time=data[i][3])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)

@app.route("/api/manager/unsend", methods=["GET", "POST"])
@cross_origin()
def manager_unsend():
    if request.method == 'GET':
        data = db.session.execute(text('select * from oorder where checked=0')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], shop_name=data[i][1], price=data[i][2], orderway=data[i][3],
                       cons_phone=data[i][4],
                       cons_name=data[i][5], cons_addre=data[i][6], create_time=data[i][8])
            Data.append(dic)

        disp_range = db.session.execute(text('select * from dispatcher')).fetchall()  # 获取所有的送货员就id，供选择
        Disp_range = []
        for i in range(len(disp_range)):
            dic = dict(disp_id=disp_range[i][0])
            Disp_range.append(dic)
        return jsonify(status=200, tabledata=Data, disp_range=Disp_range)
    if request.method == 'POST':
        rq = request.json
        order_id = rq.get('order_id')
        disp_id = rq.get('dispatcher_id')
        deliver_time = rq.get('deliver_time')
        cons_phone = db.session.execute(text('select cons_phone from oorder where order_id="%d"' % int(order_id))).first()

        db.session.execute(text('insert wuliu( order_id, cons_phone,disp_id,deliver_time) value(%d,"%s","%s","%s")' % (
        int(order_id), cons_phone[0], disp_id, deliver_time)))
        db.session.commit()
        return jsonify(status=200, msg="成功派发")

@app.route("/api/manager/sending", methods=["GET"])
@cross_origin()
def manager_sending():
    if request.method == 'GET':
        data = db.session.execute(text('select * from sending_order')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], shop_name=data[i][1], order_money=data[i][2], order_way=data[i][3],
                       cons_phone=data[i][4],
                       cons_name=data[i][5], cons_addre=data[i][6], disp_id=data[i][7], deliver_time=data[i][8])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)

@app.route("/api/manager/sended", methods=["GET"])
@cross_origin()
def manager_sended():
    if request.method == 'GET':
        data = db.session.execute(text('select * from sended_order')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], shop_name=data[i][1], order_money=data[i][2], order_way=data[i][3],
                       cons_phone=data[i][4],
                       cons_name=data[i][5], cons_addre=data[i][6], disp_id=data[i][7], deliver_time=data[i][8])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)

# 新增：更新用户信息
@app.route("/api/user/updateusermsg", methods=["POST"])
@cross_origin()
def update_user_msg():
    rq = request.json
    phone = get_token_phone(request.headers.get('token'))
    real_name = rq.get("real_name")
    sex = rq.get("sex")
    age = rq.get("age")
    mail = rq.get("mail")
    user_name = rq.get("user_name")

    db.session.execute(text('update user_msg set real_name="%s", sex="%s", age="%d", mail="%s", user_name="%s" where phone="%s"' % (
        real_name, sex, int(age), mail, user_name, phone)))
    db.session.commit()
    return jsonify(status=200, msg="信息更新成功")

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='5000')
    # 开启了debug模式
