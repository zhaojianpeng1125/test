<template>
  <div>
    <div class="header">
      欢迎光临，祝您购物愉快!
    </div>
    <div class="body">
      <el-table :data="tableData" style="width: 100%" class="table" border align="center">
        <el-table-column prop="shop_name" label="商品名称" width="200" align="center">
        </el-table-column>
        <el-table-column prop="price" label="商品单价" width="200" align="center">
        </el-table-column>
        <el-table-column prop="sale" label="月销量" width="200" align="center">
        </el-table-column>
        <el-table-column prop="operate" label="操作" width="208" align="center">
          <template slot-scope="scope">
            <el-button class="cart-button" icon="el-icon-plus" size="small" type="danger" @click="addToCart(scope.row)">加入购物车</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="text-align: center; margin-top: 20px;">
        <el-button type="info" style="background-color: #FFB6C1; color: white;" @click="showCart">查看购物车</el-button>
      </div>

      <el-dialog title="查看购物车" :visible.sync="dialog" class="dialog" width="40%">
        <div>
          <el-table :data="cart" style="width: 100%" class="table" border>
            <el-table-column prop="shop_name" label="商品名称" width="200" align="center">
            </el-table-column>
            <el-table-column prop="price" label="商品单价" width="200" align="center">
            </el-table-column>
            <el-table-column label="数量" width="200" align="center">
              <template slot-scope="scope">
                <el-input-number v-model="scope.row.quantity" @change="updateTotalPrice" :min="1"></el-input-number>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center">
              <template slot-scope="scope">
                <el-button type="danger" @click="removeFromCart(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div>总价格: {{ totalPrice }}</div>
          <div style="text-align: center; margin-top: 20px;">
            <el-button type="primary" @click="confirmPurchase">确认购买</el-button>
          </div>
        </div>
      </el-dialog>

      <el-dialog title="订单确认信息" :visible.sync="orderDialog" class="dialog" width="40%">
        <div>
          <el-form ref="orderForm" :model="orderForm" label-width="100px">
            <el-form-item label="收货人姓名">
              <el-input v-model="orderForm.cons_name"></el-input>
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="orderForm.cons_phone"></el-input>
            </el-form-item>
            <el-form-item label="收货地址">
              <el-input v-model="orderForm.cons_addre"></el-input>
            </el-form-item>
          </el-form>
          <div style="text-align: center;">
            <el-button type="primary" @click="submitOrder">提交订单</el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      dialog: false,
      orderDialog: false,
      cart: [], // 购物车数组
      totalPrice: 0, // 总价格
      orderForm: { // 订单表单数据
        cons_name: '',
        cons_phone: '',
        cons_addre: ''
      }
    };
  },
  methods: {
    addToCart(item) {
      // 查找购物车中是否已存在该商品
      const existingItem = this.cart.find(cartItem => cartItem.shop_name === item.shop_name);
      if (existingItem) {
        // 如果存在，数量加1
        existingItem.quantity += 1;
      } else {
        // 如果不存在，添加到购物车并设置数量为1
        this.cart.push({ ...item, quantity: 1 });
      }
      // 更新总价格
      this.updateTotalPrice();
    },
    showCart() {
      this.dialog = true;
    },
    removeFromCart(item) {
      // 从购物车中移除商品
      const index = this.cart.indexOf(item);
      if (index > -1) {
        this.cart.splice(index, 1);
      }
      // 更新总价格
      this.updateTotalPrice();
    },
    updateTotalPrice() {
      this.totalPrice = this.cart.reduce((total, item) => total + item.price * item.quantity, 0);
    },
    confirmPurchase() {
      // 关闭购物车对话框，打开订单确认信息对话框
      this.dialog = false;
      this.orderDialog = true;
    },
    submitOrder() {
      // 提交订单
      const orderData = {
        shop_name: this.cart.map(item => item.shop_name).join(', '),
        order_money: this.totalPrice,
        order_way: '网上订货',
        cons_name: this.orderForm.cons_name,
        cons_phone: this.orderForm.cons_phone,
        cons_addre: this.orderForm.cons_addre
      };

      this.$axios.post("/api/user/addorder", orderData).then((res) => {
        if (res.data.status === 200) {
          this.$message({
            message: "成功下单",
            type: "success",
          });
          // 清空购物车和订单表单数据
          this.cart = [];
          this.totalPrice = 0;
          this.orderForm = {
            cons_name: '',
            cons_phone: '',
            cons_addre: ''
          };
          // 关闭订单确认信息对话框
          this.orderDialog = false;
        } else {
          this.$message({
            message: "下单失败",
            type: "error",
          });
        }
      }).catch((error) => {
        console.error("提交订单失败:", error);
        this.$message({
          message: "提交订单失败",
          type: "error",
        });
      });
    },
    getdata() {
      this.$axios.get("/api/user/shop").then((res) => {
        if (res.data.status === 200) {
          this.tableData = res.data.tabledata;
        }
      }).catch(error => {
        console.error("获取数据失败:", error);
      });
    }
  },
  created() {
    this.getdata();
  },
};
</script>

<style scoped>
.header {
  width: 100%;
  height: 10%;
  text-align: center;
  line-height: 64px;
  font-size: 20px;
  font-weight: 800;
  border-bottom: 1px solid #cd9b9b;
}

.body {
  width: 62%;
  margin: auto;
  margin-top: 30px;
}

.dialog {
  text-align: center;
}

.cart-button {
  background-color: #FFB6C1; /* 淡粉色 */
  color: white;
}
</style>
