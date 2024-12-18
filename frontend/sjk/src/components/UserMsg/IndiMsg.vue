<template>
    <div>
        <div class="header">
            个人信息
        </div>
        <div class="body">
            <el-form ref="form" :model="form" label-width="20%" id="selectForm">
                <el-form-item label="用户名：" prop="dispatcher_id">
                    <span v-if="!isEditing">{{ form.user_name }}</span>
                    <el-input v-else v-model="form.user_name"></el-input>
                </el-form-item>
                <el-form-item label="真实姓名：" prop="dispatcher_name">
                    <span v-if="!isEditing">{{ form.real_name }}</span>
                    <el-input v-else v-model="form.real_name"></el-input>
                </el-form-item>
                <el-form-item label="年龄：" prop="dispatcher_phone">
                    <span v-if="!isEditing">{{ form.age }}</span>
                    <el-input v-else v-model="form.age"></el-input>
                </el-form-item>
                <el-form-item label="性别：" prop="dispatcher_phone">
                    <span v-if="!isEditing">{{ form.sex }}</span>
                    <el-input v-else v-model="form.sex"></el-input>
                </el-form-item>
                <el-form-item label="电话：" prop="dispatcher_phone">
                    <span v-if="!isEditing">{{ form.phone }}</span>
                    <el-input v-else v-model="form.phone"></el-input>
                </el-form-item>
                <el-form-item label="邮箱：" prop="dispatcher_phone">
                    <span v-if="!isEditing">{{ form.mail }}</span>
                    <el-input v-else v-model="form.mail"></el-input>
                </el-form-item>
                <el-form-item v-if="!isEditing">
                    <el-button type="primary" @click="isEditing = true">修改</el-button>
                </el-form-item>
                <el-form-item v-else>
                    <el-button type="primary" @click="saveChanges">保存</el-button>
                    <el-button @click="cancelEdit">取消</el-button>
                </el-form-item>
            </el-form>
        </div>
    </div>
</template>

<script>
export default {
    name: 'MyUserInfo',
    data() {
        return {
            isEditing: false,
            form: {
                real_name: '',
                sex: '',
                age: '',
                mail: '',
                phone: '',
                user_name: '',
            }
        }
    },
    created() {
        this.getdata()
    },
    methods: {
        getdata() {
            this.$axios.get("/api/user/usermsg").then((res) => {
                console.log(res.data);
                if (res.data.status == 200) {
                    this.form = { ...res.data.data };
                }
            }).catch(error => {
                console.error("获取用户信息失败", error);
            });
        },
        saveChanges() {
            console.log("保存的表单数据:", this.form); // 打印发送的数据

            this.$axios.post("/api/user/updateusermsg", this.form).then((res) => {
                console.log("响应数据:", res.data); // 打印响应数据
                if (res.data.status == 200) {
                    this.$message({
                        message: "信息更新成功",
                        type: "success"
                    });
                    this.isEditing = false;
                    this.getdata();
                } else {
                    this.$message({
                        message: "信息更新失败",
                        type: "error"
                    });
                }
            }).catch(error => {
                console.error("提交信息失败", error);
                this.$message({
                    message: "信息更新失败",
                    type: "error"
                });
            });
        },
        cancelEdit() {
            this.isEditing = false;
            this.getdata();
        }
    }
}
</script>

<style scoped>
.header {
    width: 100%;
    height: 10%;
    text-align: center;
    line-height: 64px;
    font-size: 20px;
    font-weight: 800;
    border-bottom: 1px solid #e3e3e3;
}

.body {
    width: 40%;
    margin-top: 30px;
    margin-left: 30px;
}

#selectForm >>> .el-form-item__label {
    font-size: 18px;
}

span {
    font-size: 18px;
}
</style>
